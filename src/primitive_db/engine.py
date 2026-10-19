import shlex

from prettytable import PrettyTable

from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def welcome():
    print("***База данных***")
    print()
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ... — создать таблицу")    # noqa: E501
    print("<command> list_tables — показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> — удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) — создать запись") # noqa: E501
    print("<command> select from <имя_таблицы> where <столбец> = <значение> — прочитать записи")    # noqa: E501
    print("<command> select from <имя_таблицы> — прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец> = <значение> — обновить запись")    # noqa: E501
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> — удалить запись")    # noqa: E501
    print("<command> info <имя_таблицы> — вывести информацию о таблице")
    print("<command> exit — выход из программы")
    print("<command> help — справочная информация")
    print()


def run():
    welcome()
    cacher = create_cacher()
    while True:
        metadata = load_metadata("db_meta.json")
        user_input = input(">>>Введите команду: ")
        args = shlex.split(user_input, posix=False)
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
            result = drop_table(metadata, args[1])
            if result is None:
                continue
            metadata = result
            save_metadata("db_meta.json", metadata)  

        elif cmd == "info":
            if len(args) < 2:
                print("Некорректное значение. Попробуйте снова.")
                continue
            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            columns = metadata[table_name]["columns"]
            data = load_table_data(table_name)
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {', '.join(columns)}")
            print(f"Количество записей: {len(data)}")             
        
        elif cmd == "select":
            if len(args) < 3 or args[1] != "from":
                print("Некорректное значение. Попробуйте снова.")
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_clause = None
            if len(args) > 3 and args[3] == "where":
                if len(args) < 7:
                    print("Некорректное значение. Попробуйте снова.")
                    continue
                where_clause = parse_where(args[4:])
                
            cache_key = (table_name, tuple(sorted(where_clause.items())) if where_clause else (table_name, None)) # noqa: E501

            data = cacher(cache_key, lambda: select(load_table_data(table_name), where_clause),) # noqa: E501

            columns = metadata[table_name]["columns"]
            col_names = [col.split(":")[0] for col in columns]

            if not data:
                print("Нет записей.")
                continue

            table = PrettyTable()
            table.field_names = col_names
            for row in data:
                table.add_row([row[col] for col in col_names])
            print(table)
        
        elif cmd == "insert":
            if len(args) < 5 or args[1] != "into" or args[3] != "values":
                print("Некорректное значение. Попробуйте снова.")
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

        
            values_str = " ".join(args[4:])
            if not values_str.startswith("(") or not values_str.endswith(")"):
                print("Некорректное значение. Попробуйте снова.")
                continue

            values_str = values_str.strip("()")
            raw_values = [v.strip() for v in values_str.split(",")]

            try:
                values = [convert_value(v) for v in raw_values]
            except ValueError:
                print("Некорректное значение. Попробуйте снова.")
                continue
            data = insert(metadata, table_name, values)
            if not data:
                continue
            save_table_data(table_name, data)
            print(f'Запись успешно добавлена в таблицу "{table_name}".')

        elif cmd == "delete":
            if len(args) < 7 or args[1] != "from" or args[3] != "where":
                print("Некорректное значение. Попробуйте снова.")
                continue
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            where_clause = parse_where(args[4:])
            data = load_table_data(table_name)

            deleted_ids = [
                row["ID"] for row in data
                if all(row[col] == val for col, val in where_clause.items())
            ]
            result = delete(data, where_clause)
            if result is None:
                continue
            data = result
            save_table_data(table_name, data)

            if deleted_ids:
                ids_str = ", ".join(str(i) for i in deleted_ids)
                print(f'Запись с ID={ids_str} успешно удалена из таблицы "{table_name}".') # noqa: E501
            else:
                print("Нет записей, подходящих под условие.")

        elif cmd == "update":
            if len(args) < 10 or args[2] != "set" or args[6] != "where":
                print("Некорректное значение. Попробуйте снова.")
                continue
            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            set_clause = parse_set(args[3:6])       
            where_clause = parse_where(args[7:])   

            data = load_table_data(table_name)
            updated_ids = [
                row["ID"] for row in data
                if all(row[col] == val for col, val in where_clause.items())
            ]

            data = update(data, set_clause, where_clause)
            save_table_data(table_name, data)

            if updated_ids:
                ids_str = ", ".join(str(i) for i in updated_ids)
                print(f'Запись с ID={ids_str} в таблице "{table_name}" успешно обновлена.') # noqa: E501
            else:
                print("Нет записей, подходящих под условие.")
        else:
            print(f"Функции {cmd} нет. Попробуйте снова.")

def convert_value(token):
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    if token in ("True", "true"):
        return True
    if token in ("False", "false"):
        return False
    return int(token)

def parse_where(tokens):
    return {tokens[0]: convert_value(tokens[2])}

def parse_set(tokens):
    return {tokens[0]: convert_value(tokens[2])}