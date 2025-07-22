from db_main import app
from shared.data import add_model, delete_model
from website.data.dev import DevToken
import sys


def create_token(name: str, valid_opt: str):
    token = DevToken.query.filter_by(name=name).first()
    if token:
        print(f"Token with name '{name}' already exists.")
        return

    choices = {
        "1": 5, "2": 15, "3": 30, "4": 60,
        "5": 90, "6": 180, "7": 365
    }
    days = choices.get(valid_opt, 30)

    token = DevToken(name, days)
    add_model(token)

    print(f"Token '{name}' created successfully.")
    print(f"Token: {token.token}")


def delete_token(name: str):
    token = DevToken.query.filter_by(name=name).first()
    if not token:
        print(f"Token with name '{name}' not found.")
        return

    delete_model(token)
    print(f"Token '{name}' deleted successfully.")


def get_all_tokens():
    tokens = DevToken.query.all()

    if not tokens:
        print("No tokens found.")
        return

    for token in tokens:
        print(f"Name: {token.name}, Created: {token.timestamp.strftime('%d.%m.%Y %H:%M')}, "
              f"Valid for: {token.days_valid} days")


def _exec(args):
    match args[0]:
        case "create_token":
            if len(args) < 3:
                print("Invalid args")
                return
            create_token(args[1], args[2])

        case "delete_token":
            if len(args) < 2:
                print("Invalid args")
                return
            delete_token(args[1])

        case "list_tokens":
            get_all_tokens()

        case _:
            print("Invalid command")


def main():
    args = sys.argv[1:]
    if len(args) < 1:
        print("Invalid args")
        return

    with app.app_context():
        _exec(args)


if __name__ == "__main__":
    main()
