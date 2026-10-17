import os

from primitive_db.utils import load_table_data


def create_table(metadata, table_name, columns):
    
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

def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    data_file = f"data/{table_name}.json"
    if os.path.exists(data_file):
        os.remove(data_file)
    return metadata

def insert(metadata, table_name, values):
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

def select(table_data, where_clause=None):
    if where_clause is None:
        return table_data

    result = []
    for row in table_data:
        if all(row[col] == val for col, val in where_clause.items()):
            result.append(row)
    return result  

def update(table_data, set_clause, where_clause):
    for row in table_data:
        if all(row[col] == val for col, val in where_clause.items()):
            for col, val in set_clause.items():
                row[col] = val
    return table_data

def delete(table_data, where_clause):
    result = []
    for row in table_data:
        if not all(row[col] == val for col, val in where_clause.items()):
            result.append(row)
    return result