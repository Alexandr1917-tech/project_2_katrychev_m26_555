import shlex

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata


def welcome():
    print("***")
    print("<command> exit — выйти из программы")
    print("<command> help — справочная информация")
    print("Введите команду: ")


def run():
    while True:
        metadata = load_metadata("db_meta.json")
        user_input = input(">>>Введите команду: ")
        args = shlex.split(user_input)
        if not args:
            continue
        cmd = args[0]
        if cmd == "exit":
            print("Выход из программы.")
            break
        elif cmd == "help":
            welcome()
        elif cmd == "list_tables":
            if not metadata:
                print("Нет таблиц")
            else:
                for table in metadata:
                    print(f"- {table}")
        elif cmd == "create_table":
            if len(args) < 3:
                print("Некорректное значение. Попробуйте снова.")
                continue
            metadata = create_table(metadata, args[1], args[2:])
            save_metadata("db_meta.json", metadata)     

        elif cmd == "drop_table":
            if len(args) < 2:
                print("Некорректное значение. Попробуйте снова.")
                continue
            metadata = drop_table(metadata, args[1])
            save_metadata("db_meta.json", metadata)           
        else:
            print(f"Функции {cmd} нет. Попробуйте снова.")
