from random import randint, choice
from threading import Thread
import atexit as at_exit
from time import sleep as wait
from faker import Faker
from DB import connection
from user_service import user_service
from neo import Tags


class UserEmulation(Thread):
    def __init__(self, username, receiver, delay):
        Thread.__init__(self)
        user_service.register(username)
        self.user_id = user_service.sign_in(username)
        self.receiver = receiver
        self.username = username
        self.faker = Faker()
        self.delay = delay

    def run(self):
        while True:
            message_text = self.faker.sentence(nb_words=5)
            user_service.create_message(message_text, self.user_id, self.receiver, UserEmulation.get_random_tags())

            print(f"Sender: ==> {self.username} <==")
            print(f"Receiver: ==> {self.receiver} <==")
            print(f"{message_text}\n")
            wait(self.delay)

    @staticmethod
    def get_random_tags():
        num = randint(0, len(Tags))
        tags = []
        for i in range(num):
            tag = choice(list(Tags)).name
            if tag not in tags:
                tags.append(tag)
        return tags


def main():
    def exit_handler():
        online_users = connection.smembers("online:")
        connection.srem("online:", list(online_users))

    at_exit.register(exit_handler)

    faker = Faker()
    users_count = 30
    users = [faker.name() in range(users_count)]

    for user in users:
        receiver = users[randint(0, len(users) - 1)]
        user_emulation = UserEmulation(user, receiver, randint(1, 10))
        user_emulation.start()


if __name__ == "__main__":
    main()
