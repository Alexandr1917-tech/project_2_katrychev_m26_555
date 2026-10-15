## Управление таблицами

- `create_table <имя> <столбец1:тип> ...` — создать таблицу
- `drop_table <имя>` — удалить таблицу
- `list_tables` — список таблиц
- `help` — справка
- `exit` — выход

Пример:

```

>>>Введите команду: create_table users name:str age:int
Таблица "users" успешно создана.
>>>Введите команду: list_tables
- users
>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```