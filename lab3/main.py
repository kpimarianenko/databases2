from neo import neo4j
from CUI import CUI


def main():
    while True:
        choice = CUI.main_menu()

        if choice == 1:
            CUI.print_array("Users by tags", neo4j.get_users_by_tags(input("Enter tags: ")))

        elif choice == 2:
            CUI.print_array("Users by chain length", neo4j.get_users_by_chain_length(int(input("Enter chain length: "))))

        elif choice == 3:
            CUI.print_chain(
                neo4j.get_shortest_users_chain(
                    input("Enter first username: "),
                    input("Enter second username: ")
                )
            )

        elif choice == 4:
            CUI.print_array("Spam only", neo4j.get_users_with_spam_messages_only())

        elif choice == 5:
            CUI.print_array("Unrelated users", neo4j.get_unrelated_users_by_tags(input("Enter tags: ")))

        elif choice == 0:
            print('bye')
            break

        else:
            print("Invalid option. Try again")


if __name__ == "__main__":
    main()
