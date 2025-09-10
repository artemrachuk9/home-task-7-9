import pickle
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Birthday must be in DD.MM.YYYY format.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone number not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(phone.value for phone in self.phones) if self.phones else "No phones"
        birthday = self.birthday.value if self.birthday else "No birthday"
        return f"{self.name.value}: {phones}, Birthday: {birthday}"

class AddressBook(dict):
    def add_record(self, record):
        self[record.name.value] = record

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                delta = (bday_this_year - today).days
                if delta <= 7:
                    congrats_date = bday_this_year
                    if congrats_date.weekday() >= 5:
                        congrats_date += timedelta(days=(7 - congrats_date.weekday()))
                    upcoming.append((record.name.value, congrats_date.strftime("%d.%m.%Y")))
        return upcoming

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError, AttributeError) as e:
            return f"Error: {e}"
    return wrapper

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.get(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    return f"Contact {name} updated."

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.get(name)
    record.change_phone(old_phone, new_phone)
    return f"Phone number for {name} updated."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.get(name)
    return f"{name}: {', '.join(phone.value for phone in record.phones)}"

@input_error
def show_all(book):
    return "\n".join(str(record) for record in book.values())

@input_error
def add_birthday_handler(args, book):
    name, birthday = args
    record = book.get(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_birthday(birthday)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.get(name)
    if record.birthday:
        return f"{name}'s birthday: {record.birthday.value}"
    return f"No birthday set for {name}."

@input_error
def upcoming_birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{name}: {date}" for name, date in upcoming)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()

    commands = {
        "add": add_contact,
        "change": change_contact,
        "phone": show_phone,
        "all": show_all,
        "add-birthday": add_birthday_handler,
        "show-birthday": show_birthday,
        "birthdays": upcoming_birthdays,
    }

    print("Hello! I am your assistant bot.")
    while True:
        user_input = input("Enter a command: ").strip().split()
        if not user_input:
            continue
        command, *args = user_input
        command = command.lower()

        if command in ["close", "exit"]:
            save_data(book)
            print("Goodbye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command in commands:
            handler = commands[command]
            if command in ["all", "birthdays"]:
                print(handler(book))
            else:
                print(handler(args, book))
        else:
            print("Unknown command. Try again.")

if __name__ == "__main__":
    main()
