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
    return metadata