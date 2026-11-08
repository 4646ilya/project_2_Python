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


def check_value_type(value, expected_type):
    """Проверяет, что значение соответствует ожидаемому типу."""
    if expected_type == "bool":
        return isinstance(value, bool)
    if expected_type == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, str)


def insert(metadata, table_name, table_data, values):
    """Добавляет запись в данные таблицы.

    Генерирует ID, валидирует типы. Возвращает запись или None при ошибке.
    """
    columns = metadata.get(table_name, {})
    data_columns = [name for name in columns if name != ID_COLUMN]
    if len(values) != len(data_columns):
        print(
            f"Некорректное значение: ожидалось {len(data_columns)} значений,"
            f" получено {len(values)}. Попробуйте снова."
        )
        return None
    new_id = max((record.get(ID_COLUMN, 0) for record in table_data), default=0) + 1
    record = {ID_COLUMN: new_id}
    for column_name, value in zip(data_columns, values):
        if not check_value_type(value, columns[column_name]):
            print(
                f"Некорректное значение: для столбца \"{column_name}\""
                f" ожидался тип {columns[column_name]}. Попробуйте снова."
            )
            return None
        record[column_name] = value
    table_data.append(record)
    return record


def records_match(record, where_clause):
    """Проверяет, подходит ли запись под условие where."""
    if where_clause is None:
        return True
    return all(
        record.get(column) == value for column, value in where_clause.items()
    )


def select(table_data, where_clause=None):
    """Возвращает записи, подходящие под условие, или все записи."""
    return [record for record in table_data if records_match(record, where_clause)]


def update(table_data, metadata_columns, set_clause, where_clause):
    """Обновляет поля записей по условию.

    Возвращает список обновлённых записей или None при ошибке валидации.
    """
    for column_name, value in set_clause.items():
        if column_name == ID_COLUMN or column_name not in metadata_columns:
            print(f'Некорректное значение: столбца "{column_name}" нет в таблице.')
            return None
        if not check_value_type(value, metadata_columns[column_name]):
            print(
                f"Некорректное значение: для столбца \"{column_name}\""
                f" ожидался тип {metadata_columns[column_name]}. Попробуйте снова."
            )
            return None
    updated = []
    for record in table_data:
        if records_match(record, where_clause):
            record.update(set_clause)
            updated.append(record)
    return updated


def delete(table_data, where_clause):
    """Удаляет записи по условию. Возвращает список удалённых."""
    kept = []
    deleted = []
    for record in table_data:
        if records_match(record, where_clause):
            deleted.append(record)
        else:
            kept.append(record)
    table_data[:] = kept
    return deleted
