import atexit as at_exit

from user_service import user_service
from CUI import CUI


def signed_in(user_id) -> bool:
    return user_id != -1


def main():
    current_user_id = -1
    error_message = "Invalid action. Try again"

    def exit_handler():
        if signed_in(current_user_id):
            user_service.sign_out(current_user_id)

    at_exit.register(exit_handler)

    while True:
        if not signed_in(current_user_id):
            print()
            choice = CUI.auth_menu()
            login_message = "Enter your login: "

            if choice == 1:
                login = input(login_message)
                user_service.register(login)
                current_user_id = user_service.sign_in(login)
            elif choice == 2:
                login = input(login_message)
                current_user_id = user_service.sign_in(login)
            elif choice == 3:
                break
            else:
                print(error_message)

        else:
            print()
            choice = CUI.main_menu()

            if choice == 1:
                message = input("Enter message text: ")
                receiver = input("Enter receiver username: ")

                if user_service.create_message(message, current_user_id, receiver):
                    print("Sending ...")
            elif choice == 2:
                user_service.print_messages(current_user_id)
            elif choice == 3:
                user_service.print_messages_statistics(current_user_id)
            elif choice == 4:
                user_service.sign_out(current_user_id)
                current_user_id = -1
            else:
                print(error_message)


if __name__ == "__main__":
    main()
