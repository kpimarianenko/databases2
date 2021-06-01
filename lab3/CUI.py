class CUI:
    choiceMessage = "Choose your next action: "

    @staticmethod
    def main_menu() -> int:
        print("[1] => Get messages by tag")
        print("[2] => Get users by relation chain length")
        print("[3] => Get shortest chain between users")
        print("[4] => Get users with spam messages only")
        print("[5] => Get unrelated tagged messages")
        print("\n[0] => Exit")
        return int(input(CUI.choiceMessage))

    @staticmethod
    def get_tags() -> int:
        print("[1] Add a tag")
        print("[2] Exit")
        return int(input("Enter your choice: "))

    @staticmethod
    def print_array(title, array):
        print(f">>> {title} <<<")
        count = 1
        for item in array:
            print(f"[{count}] => {item}")
            count += 1

    @staticmethod
    def print_chain(array):
        way = ""
        for item in array:
            way += f"{item} =>"
        print(way[:-3])

