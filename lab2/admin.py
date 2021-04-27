from DB import connection
from CUI import CUI


def main():
    error_message = "Invalid action. Try again"

    while True:
        print()
        choice = CUI.admin_menu()

        if choice == 1:
            online_users = connection.smembers("online:")
            print("Users online:")
            for index, user in enumerate(online_users):
                print(f"{index + 1}. {user}")

        elif choice == 2:
            senders = connection.zrange("sent:", 0, 4, desc=True, withscores=True)
            print("Top senders:")
            for index, sender in enumerate(senders):
                username = sender[0].replace("user:", "")
                messages_count = sender[1]
                print(f"{index + 1}. {username}: {int(messages_count)} messages")

        elif choice == 3:
            spammers = connection.zrange("spam:", 0, 4, desc=True, withscores=True)
            print("Top spammers:")
            for index, spammer in enumerate(spammers):
                username = spammer[0].replace("user:", "")
                messages_count = spammer[1]
                print(f"{index + 1}. {username}: {int(messages_count)} messages")

        elif choice == 4:
            break
        else:
            print(error_message)


if __name__ == '__main__':
    main()
