from neo4j import GraphDatabase
from enum import Enum


class Tags(Enum):
    work = 1,
    study = 2,
    private = 3

    @classmethod
    def has_member(cls, value):
        return value in Tags._member_names_


class Neo4J:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123"))

    def close(self):
        self.driver.close()

    def truncate(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def register(self, username, redis_id):
        with self.driver.session() as session:
            session.run("MERGE (u:user {name: $username, redis_id: $redis_id}) ON CREATE SET u.online = false",
                        username=username, redis_id=redis_id)

    def sign_in(self, redis_id):
        with self.driver.session() as session:
            session.run("MATCH (u:user {redis_id: $redis_id}) SET u.online = true", redis_id=redis_id)

    def sign_out(self, redis_id):
        with self.driver.session() as session:
            session.run("MATCH (u:user {redis_id: $redis_id}) SET u.online = false", redis_id=redis_id)

    def get_users(self):
        with self.driver.session() as session:
            return Neo4J.get_list_from_value(session.run("MATCH (u:user) RETURN u"), 'name')

    def get_users_with_spam_messages_only(self):
        with self.driver.session() as session:
            res = session.run("MATCH p = (u1:user)-[]-(u2:user) WHERE u1 <> u2 AND all(x in relationships(p)"
                              "WHERE x.all = x.spam) RETURN u1, u2")
            return Neo4J.get_list_from_pair(res, 'name')

    def get_users_by_chain_length(self, length):
        with self.driver.session() as session:
            res = session.run(f"MATCH p = (u1:user)-[*]-(u2:user) WHERE u1 <> u2 AND reduce(total_len = 0, r"
                              f"IN relationships(p)| total_len + size(r.all)) = {length} RETURN u1, u2")
            return self.get_list_from_pair(res, 'name')

    def get_users_by_tags(self, tags):
        return self.get_list_from_value(self.request_users_by_tags(tags), 'name')

    def get_unrelated_users_by_tags(self, tags):
        list_of_names = self.get_list_from_value(self.request_users_by_tags(tags), 'name')
        unrelated_users = []
        for name1 in list_of_names:
            group = [name1]
            for name2 in list_of_names:
                if name1 != name2:
                    res = self.is_users_related(name1, name2)
                    if not res and name1 not in group:
                        group.append(name2)
            unrelated_users.append(group)

        return unrelated_users

    def request_users_by_tags(self, tags):
        with self.driver.session() as session:
            tags = tags.split(", ")
            for tag in tags:
                if not Tags.has_member(tag):
                    raise ValueError(f"Tag: {tag} doesnt exist")

            query = "MATCH (u:user)-[r:messages]-() WHERE"
            for tag in tags:
                query += f" \'{tag}\' IN r.tags AND"

            query = query[:-3] + "RETURN u"
            return session.run(query)

    def is_users_related(self, username1, username2):
        with self.driver.session() as session:
            res = session.run("MATCH  (u1:user {name: $username1}), (u2:user {name: $username2}) "
                              "RETURN EXISTS((u1)-[:messages]-(u2))", username1=username1, username2=username2)
            return res.single()[0]

    def get_shortest_users_chain(self, username1, username2):
        users = self.get_users()
        if username1 not in users or username2 not in users:
            raise ValueError('Invalid users names')
        with self.driver.session() as session:
            shortest_chain = session.run("MATCH p = shortestPath((u1:user)-[*..10]-(u2:user)) WHERE"
                                         "u1.name = $username1 AND u2.name = $username2 RETURN p", username1=username1,
                                         username2=username2)
            if shortest_chain.peek() is None:
                raise Exception(f"Cannot find way between {username1} and {username2}")
            for record in shortest_chain:
                nodes = record[0].nodes
                chain = []
                for node in nodes:
                    chain.append(node._properties['name'])
                return chain

    def create_message(self, sender_id, consumer_id, message: dict):
        with self.driver.session() as session:
            try:
                messages_id = session.write_transaction(self.create_related_message, int(sender_id),
                                                        int(consumer_id), message["id"])
                for tag in message["tags"]:
                    session.write_transaction(self.tag_messages, messages_id, tag)
            except Exception as e:
                print(str(e))

    @staticmethod
    def create_related_message(tx, sender_id, consumer_id, message_id):
        return tx.run("MATCH(a: user {redis_id: $sender_id}), (b:user {redis_id: $consumer_id})"
                      "MERGE(a) - [r: messages]->(b) ON CREATE SET r.all = [$message_id], r.spam = [], r.tags = []"
                      "ON MATCH SET r.all = r.all + $message_id RETURN id(r)", sender_id=sender_id,
                      consumer_id=consumer_id, message_id=message_id).single()[0]

    @staticmethod
    def tag_messages(tx, messages_id, tag):
        tx.run("MATCH ()-[r]-() where ID(r) = $messages_id FOREACH(x in CASE WHEN $tag in r.tags THEN [] ELSE [1] END"
               "| SET r.tags = coalesce(r.tags,[]) + $tag)", messages_id=messages_id, tag=tag)

    def send_message(self, redis_id):
        with self.driver.session() as session:
            session.run("MATCH (m:messages {redis_id: $redis_id }) SET m.delivered = true", redis_id=redis_id)

    def add_message_to_spam(self, redis_id):
        with self.driver.session() as session:
            session.run("MATCH (u1:user)-[r:messages]->(u2:user) WHERE $redis_id IN r.all AND NOT $redis_id IN r.spam "
                        "SET r.spam = r.spam + $redis_id", redis_id=redis_id)

    @staticmethod
    def get_list_from_pair(res, key):
        initial_list = list(dict.fromkeys(list(res)))
        final_list = []
        for el in initial_list:
            list_el = list(el)
            if list_el not in final_list and list_el[::-1] not in final_list:
                final_list.append(el)

        return [[el[0]._properties[key], el[1]._properties[key]] for el in final_list]

    @staticmethod
    def get_list_from_value(res, key):
        initial_list = list(dict.fromkeys(list(res)))
        return [el[0]._properties[key] for el in initial_list]


neo4j = Neo4J()
