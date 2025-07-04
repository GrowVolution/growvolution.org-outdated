from dotenv import load_dotenv
load_dotenv()

from db_manage import app
from website.data import add_model, delete_model
from website.data.dev import DevToken


def print_main_menu():
    print("1 - create a new token")
    print("2 - delete a token")
    print("3 - list all tokens")
    print("4 - exit\n")


def print_time_valid_menu():
    print("How long should the token be valid?\n")

    print("\t1 - 5 days")
    print("\t2 - 15 days")
    print("\t3 - 30 days (default)")
    print("\t4 - 60 days")
    print("\t5 - 90 days")
    print("\t6 - 180 days")
    print("\t7 - 365 days")


def create_token():
    name = input("Enter a unique name: ")

    token = DevToken.query.filter_by(name=name).first()
    if token:
        print(f"Token with name '{name}' already exists.")
        return

    print_time_valid_menu()
    choice = input("\t> ")

    choices = {
        "1": 5, "2": 15, "3": 30, "4": 60,
        "5": 90, "6": 180, "7": 365
    }
    days = choices.get(choice, 30)

    print('Creating token...')

    token = DevToken(name, days)
    add_model(token)

    print(f"Token '{name}' created successfully.")
    print(f"Token: {token.token}")


def delete_token():
    name = input("Enter the name of the token to delete: ")

    token = DevToken.query.filter_by(name=name).first()
    if not token:
        print(f"Token with name '{name}' not found.")
        return

    delete_model(token)
    print(f"Token '{name}' deleted successfully.")


def print_all_tokens():
    tokens = DevToken.query.all()

    if not tokens:
        print("No tokens found.")
        return

    for token in tokens:
        print(f"Name: {token.name}, Token: {token.token}, "
              f"Created: {token.timestamp.strftime('%d.%m.%Y %H:%M')}, "
              f"Valid for: {token.days_valid} days")


def main():
    print("\n\nGrowVolution 2025 - GNU General Public License")
    print("Dev Token Management: Enter the number of the action you want to perform.\n")
    print_main_menu()

    while True:
        cmd = input("> ")

        if cmd == "1":
            create_token()

        elif cmd == "2":
            delete_token()

        elif cmd == "3":
            print_all_tokens()

        elif cmd == "4":
            print("\nThank you for playing the game of life, bye!")
            break

        else:
            print("Invalid option! You can just:\n")
            print_main_menu()


if __name__ == "__main__":
    with app.app_context():
        main()
