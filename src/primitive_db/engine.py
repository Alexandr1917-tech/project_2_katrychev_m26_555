import shlex

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata


def welcome():
    print("***База данных***")
    print()
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ... — создать таблицу")
    print("<command> list_tables — показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> — удалить таблицу")
    print("<command> exit — выход из программы")
    print("<command> help — справочная информация")
    print()


def run():
    welcome()
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

