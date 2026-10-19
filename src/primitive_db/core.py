import os

from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создаёт новую таблицу."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    
    allowed_types = {"int", "str", "bool"}
    for col in columns:
        col_type = col.split(":")[-1]
        if col_type not in allowed_types:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return metadata

    full_columns = ["ID:int"] + columns
    metadata[table_name] = {"columns": full_columns}
    return metadata    

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    data_file = f"data/{table_name}.json"
    if os.path.exists(data_file):
        os.remove(data_file)
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return []

    columns = metadata[table_name]["columns"]

    if len(values) != len(columns) - 1:
        print(f"Ошибка: Ожидается {len(columns) - 1} значений, получено {len(values)}.")
        return [] 

    type_map = {"str": str, "int": int, "bool": bool}
    
    for col_schema, value in zip(columns[1:], values):
        expected_type_name = col_schema.split(":")[-1]
        expected_type = type_map[expected_type_name]
        if not isinstance(value, expected_type):
            print(f"Ошибка: Неверный тип {value!r}. Ожидается {expected_type_name}.")
            return []

    data = load_table_data(table_name)

    if not data:
        new_id = 1
    else:
        new_id = max(row["ID"] for row in data) + 1   

    col_names = [col.split(":")[0] for col in columns]   # ["ID", "name", "age"]
    new_row = {"ID": new_id}
    for name, value in zip(col_names[1:], values):
        new_row[name] = value
    data.append(new_row)
    return data   

@log_time
def select(table_data, where_clause=None):
    """Возвращает записи по условию (или все, если условие не задано)."""
    if where_clause is None:
        return table_data

    result = []
    for row in table_data:
        if all(row[col] == val for col, val in where_clause.items()):
            result.append(row)
    return result  

@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет поля в записях, подходящих под условие."""
    for row in table_data:
        if all(row[col] == val for col, val in where_clause.items()):
            for col, val in set_clause.items():
                row[col] = val
    return table_data

@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи, подходящие под условие."""
    result = []
    for row in table_data:
        if not all(row[col] == val for col, val in where_clause.items()):
            result.append(row)
    return result