from DB import connection


class UsersService:
    def __init__(self, _connection):
        self.connection = _connection

    def register(self, username):
        if self.connection.hget("users:", username):
            return None

        user_id = self.connection.incr("user:id:")
        pipeline = self.connection.pipeline(True)
        pipeline.hset("users:", username, user_id)

        pipeline.hmset(f"user:{user_id}", {
            "login": username,
            "id": user_id,
            "queue": 0,
            "checking": 0,
            "blocked": 0,
            "sent": 0,
            "delivered": 0
        })

        pipeline.execute()
        return user_id

    def sign_in(self, username) -> int:
        user_id = self.connection.hget("users:", username)

        if not user_id:
            print(f"[error]: user {username} does not exist")
            return -1
        else:
            login, *rest = connection.hmget(f"user:{user_id}", ["login"])
            self.connection.publish("users", f"User {login} signed in")

        self.connection.sadd("online:", username)
        return int(user_id)

    def sign_out(self, user_id) -> int:
        login, *rest = self.connection.hmget(f"user:{user_id}", ["login"])
        self.connection.publish("users", f"User {login} signed out")

        return self.connection.srem("online:", login)

    def create_message(self, message_text, sender_id, receiver) -> int:
        message_id = self.connection.incr("message:id:")
        receiver_id = self.connection.hget("users:", receiver)

        if not receiver_id:
            print(f"[error]: unable to send message. user {receiver} does not exist")
            return

        pipeline = self.connection.pipeline(True)
        pipeline.hmset(f"message:{message_id}", {
            "text": message_text,
            "id": message_id,
            "sender_id": sender_id,
            "consumer_id": receiver_id,
            "status": "created"
        })
        pipeline.lpush("queue:", message_id)
        pipeline.hmset(f"message:{message_id}", {"status": "queue"})
        login, *rest = self.connection.hmget(f"user:{sender_id}", ["login"])
        pipeline.zincrby("sent:", 1, f"user:{login}")
        pipeline.hincrby(f"user:{sender_id}", "queue", 1)
        pipeline.execute()

        return message_id

    def print_messages(self, user_id):
        messages = self.connection.smembers(f"sentto:{user_id}")
        for message_id in messages:
            sender_id, text, status = self.connection.hmget(f"message:{message_id}", ["sender_id", "text", "status"])
            login, *rest = self.connection.hmget(f"user:{sender_id}", ["login"])
            print(f"From: {login} - {text}")
            if status != "delivered":
                pipeline = self.connection.pipeline(True)
                pipeline.hset(f"message:{message_id}", "status", "delivered")
                pipeline.hincrby(f"user:{sender_id}", "sent", -1)
                pipeline.hincrby(f"user:{sender_id}", "delivered", 1)
                pipeline.execute()


    def print_messages_statistics(self, user_id):
        queue, checking, blocked, sent, delivered = connection.hmget(f"user:{user_id}",
                                                                     ["queue", "checking", "blocked", "sent",
                                                                      "delivered"])
        print(f"[in queue]: {queue}")
        print(f"[checking]: {checking}")
        print(f"[blocked]: {blocked}")
        print(f"[sent]: {sent}")
        print(f"[delivered]: {delivered}")


user_service = UsersService(connection)
