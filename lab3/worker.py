from datetime import datetime
from threading import Thread
from random import randint, random
from time import sleep as wait
import logging

from neo import neo4j
from DB import connection


logging.basicConfig(filename="logs.txt", level=logging.INFO)


class EventListener(Thread):
    def __init__(self, _connection):
        Thread.__init__(self)
        self.connection = _connection

    def run(self):
        pub_sub = self.connection.pubsub()
        pub_sub.subscribe(["users", "spam"])

        for item in pub_sub.listen():
            if item['type'] == 'message':
                logging.info(f"[{datetime.now()}]: {item['data']}")


class Worker(Thread):
    def __init__(self, _connection, delay, neo):
        Thread.__init__(self)
        self.connection = _connection
        self.delay = delay
        self.neo = neo

    def run(self):
        while True:
            _, message_id = self.connection.brpop("queue:")
            if message_id:
                self.connection.hset(f"message:{message_id}", "status", "checking")

                sender_id, consumer_id = self.connection.hmget(f"message:{message_id}", ["sender_id", "consumer_id"])
                self.connection.hincrby(f"user:{sender_id}", "queue", -1)
                self.connection.hincrby(f"user:{sender_id}", "checking", 1)

                wait(self.delay)
                is_spam = random() > 0.5
                pipeline = self.connection.pipeline(True)
                pipeline.hincrby(f"user:{sender_id}", "checking", -1)

                if is_spam:
                    username, *rest = self.connection.hmget(f"user:{sender_id}", ["login"])
                    pipeline.zincrby("spam:", 1, f"user:{username}")
                    pipeline.hset(f"message:{message_id}", "status", "blocked")
                    pipeline.hincrby(f"user:{sender_id}", "blocked", 1)

                    message_text, *rest = self.connection.hmget(f"message:{message_id}", ["text"])
                    pipeline.publish("spam", f"User {username} sent spam message: '{message_text}'")
                    self.neo.add_message_to_spam(message_id)
                else:
                    pipeline.hset(f"message:{message_id}", "status", "sent")
                    pipeline.hincrby(f"user:{sender_id}", "sent", 1)
                    pipeline.sadd(f"sentto:{consumer_id}", message_id)

                pipeline.execute()
            else:
                print("[error]: queue is empty")


def main():
    listener = EventListener(connection)
    listener.start()

    handlers_count = 3

    for _ in range(handlers_count):
        worker = Worker(connection, randint(1, 5), neo4j)
        worker.start()


if __name__ == "__main__":
    main()
