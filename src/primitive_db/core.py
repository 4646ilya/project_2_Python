from .constants import ID_COLUMN, ID_TYPE, VALID_TYPES


def create_table(metadata, table_name, columns):
    """Создаёт таблицу в метаданных.

    Автоматически добавляет столбец ID:int в начало.
    Возвращает обновлённый словарь метаданных.
    """
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    for col_name, col_type in columns.items():
        if col_type not in VALID_TYPES:
            print(
                f"Некорректное значение: {col_name}:{col_type}."
                " Попробуйте снова."
            )
            return metadata
    full_columns = {ID_COLUMN: ID_TYPE, **columns}
    metadata[table_name] = full_columns
    columns_str = ", ".join(f"{n}:{t}" for n, t in full_columns.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных.

    Возвращает обновлённый словарь метаданных.
    """
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Возвращает список имён таблиц."""
    return list(metadata.keys())
