import shlex

import prompt
from prettytable import PrettyTable

from . import core, parser
from .constants import META_FILE
from .utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Печатает справку по текущему режиму."""
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...)"
        " - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение>"
        " - прочитать записи по условию"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение>"
        " where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение>"
        " - удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome():
    """Приветствует пользователя и показывает список команд."""
    name = prompt.string("May I have your name? ")
    print(f"Hello, {name}!")
    print_help()


def parse_columns(raw_columns):
    """Разбирает аргументы вида "имя:тип" в словарь столбцов."""
    parsed = {}
    for column in raw_columns:
        name, sep, col_type = column.partition(":")
        if not sep or not name or not col_type:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return None
        parsed[name] = col_type
    return parsed


def get_metadata():
    """Загружает метаданные базы."""
    return load_metadata(META_FILE)


def ensure_table(metadata, table_name):
    """Проверяет существование таблицы, печатает ошибку при отсутствии."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return False
    return True


def print_table(records, columns):
    """Печатает записи в виде красивой таблицы."""
    pretty = PrettyTable()
    pretty.field_names = list(columns.keys())
    for record in records:
        pretty.add_row([record.get(name) for name in columns])
    print(pretty)


def run_create_table(args):
    """Обрабатывает команду create_table."""
    if len(args) < 3:
        print("Некорректное значение: мало аргументов. Попробуйте снова.")
        return
    columns = parse_columns(args[2:])
    if columns is None:
        return
    metadata = get_metadata()
    metadata = core.create_table(metadata, args[1], columns)
    save_metadata(META_FILE, metadata)


def run_drop_table(args):
    """Обрабатывает команду drop_table."""
    if len(args) != 2:
        print("Некорректное значение: мало аргументов. Попробуйте снова.")
        return
    metadata = get_metadata()
    metadata = core.drop_table(metadata, args[1])
    save_metadata(META_FILE, metadata)


def run_list_tables():
    """Обрабатывает команду list_tables."""
    tables = core.list_tables(get_metadata())
    if not tables:
        print("В базе пока нет таблиц.")
    for table_name in tables:
        print(f"- {table_name}")


def run_insert(user_input, args):
    """Обрабатывает команду insert."""
    if len(args) < 4 or args[1] != "into" or args[3] != "values":
        print("Некорректное значение. Попробуйте снова.")
        return
    table_name = args[2]
    metadata = get_metadata()
    if not ensure_table(metadata, table_name):
        return
    values = parser.parse_values(user_input.partition("values")[2])
    if values is None:
        print("Некорректное значение. Попробуйте снова.")
        return
    table_data = load_table_data(table_name)
    record = core.insert(metadata, table_name, table_data, values)
    if record is None:
        return
    save_table_data(table_name, table_data)
    print(f'Запись с ID={record["ID"]} успешно добавлена в таблицу "{table_name}".')


def run_select(user_input, args):
    """Обрабатывает команду select."""
    if len(args) < 3 or args[1] != "from":
        print("Некорректное значение. Попробуйте снова.")
        return
    table_name = args[2]
    metadata = get_metadata()
    if not ensure_table(metadata, table_name):
        return
    _, sep, condition = user_input.partition(" where ")
    where_clause = None
    if sep:
        where_clause = parser.parse_where(condition)
        if where_clause is None:
            print("Некорректное значение. Попробуйте снова.")
            return
    table_data = load_table_data(table_name)
    records = core.select(table_data, where_clause)
    print_table(records, metadata[table_name])


def run_update(user_input, args):
    """Обрабатывает команду update."""
    if len(args) < 4 or args[2] != "set":
        print("Некорректное значение. Попробуйте снова.")
        return
    table_name = args[1]
    metadata = get_metadata()
    if not ensure_table(metadata, table_name):
        return
    set_raw, sep_where, where_raw = user_input.partition(" set ")[2].partition(
        " where "
    )
    if not sep_where:
        print("Некорректное значение: нет условия where. Попробуйте снова.")
        return
    set_clause = parser.parse_where(set_raw)
    where_clause = parser.parse_where(where_raw)
    if set_clause is None or where_clause is None:
        print("Некорректное значение. Попробуйте снова.")
        return
    table_data = load_table_data(table_name)
    updated = core.update(table_data, metadata[table_name], set_clause, where_clause)
    if updated is None:
        return
    if not updated:
        print("Записи не найдены.")
        return
    save_table_data(table_name, table_data)
    for record in updated:
        print(
            f'Запись с ID={record["ID"]} в таблице "{table_name}" успешно обновлена.'
        )


def run_delete(user_input, args):
    """Обрабатывает команду delete."""
    if len(args) < 2 or args[1] != "from":
        print("Некорректное значение. Попробуйте снова.")
        return
    table_name = args[2]
    metadata = get_metadata()
    if not ensure_table(metadata, table_name):
        return
    _, sep, condition = user_input.partition(" where ")
    if not sep:
        print("Некорректное значение: нет условия where. Попробуйте снова.")
        return
    where_clause = parser.parse_where(condition)
    if where_clause is None:
        print("Некорректное значение. Попробуйте снова.")
        return
    table_data = load_table_data(table_name)
    deleted = core.delete(table_data, where_clause)
    if deleted is None:
        return
    if not deleted:
        print("Записи не найдены.")
        return
    save_table_data(table_name, table_data)
    for record in deleted:
        print(f'Запись с ID={record["ID"]} успешно удалена из таблицы "{table_name}".')


def run_info(args):
    """Обрабатывает команду info."""
    if len(args) != 2:
        print("Некорректное значение: мало аргументов. Попробуйте снова.")
        return
    table_name = args[1]
    metadata = get_metadata()
    if not ensure_table(metadata, table_name):
        return
    columns = ", ".join(
        f"{name}:{col_type}" for name, col_type in metadata[table_name].items()
    )
    table_data = load_table_data(table_name)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns}")
    print(f"Количество записей: {len(table_data)}")


def run():
    """Основной цикл программы."""
    while True:
        user_input = prompt.string("Введите команду: ")
        try:
            args = shlex.split(user_input)
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
            continue
        if not args:
            continue
        command = args[0]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            run_create_table(args)
        elif command == "drop_table":
            run_drop_table(args)
        elif command == "list_tables":
            run_list_tables()
        elif command == "insert":
            run_insert(user_input, args)
        elif command == "select":
            run_select(user_input, args)
        elif command == "update":
            run_update(user_input, args)
        elif command == "delete":
            run_delete(user_input, args)
        elif command == "info":
            run_info(args)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
