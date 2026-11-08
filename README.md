## Управление таблицами

Запустите базу командой `uv run database`.

- `create_table <имя> <столбец:тип> ...` — создать таблицу (ID добавляется автоматически)
- `list_tables` — показать список таблиц
- `drop_table <имя>` — удалить таблицу
- `help` — справка, `exit` — выход

Пример:

    create_table users name:str age:int is_active:bool
    Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
