import shlex

import prompt

from . import core
from .constants import META_FILE
from .utils import load_metadata, save_metadata


def print_help():
    """Печатает справку по текущему режиму."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome():
    """Приветствует пользователя и показывает список команд."""
    name = prompt.string("May I have your name? ")
    print(f"Hello, {name}!")
    print_help()


def parse_command(user_input):
    """Разбирает строку ввода на команду и аргументы.

    Возвращает список строк или None при ошибке разбора.
    """
    try:
        args = shlex.split(user_input)
    except ValueError as error:
        print(f"Некорректное значение: {error}. Попробуйте снова.")
        return None
    if not args:
        return None
    return args


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


def run():
    """Основной цикл программы."""
    while True:
        args = parse_command(prompt.string("Введите команду: "))
        if args is None:
            continue
        command, arguments = args[0], args[1:]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            if len(arguments) < 2:
                print("Некорректное значение: мало аргументов. Попробуйте снова.")
                continue
            columns = parse_columns(arguments[1:])
            if columns is None:
                continue
            metadata = load_metadata(META_FILE)
            metadata = core.create_table(metadata, arguments[0], columns)
            save_metadata(META_FILE, metadata)
        elif command == "list_tables":
            tables = core.list_tables(load_metadata(META_FILE))
            if not tables:
                print("В базе пока нет таблиц.")
            for table_name in tables:
                print(f"- {table_name}")
        elif command == "drop_table":
            if len(arguments) != 1:
                print("Некорректное значение: мало аргументов. Попробуйте снова.")
                continue
            metadata = load_metadata(META_FILE)
            metadata = core.drop_table(metadata, arguments[0])
            save_metadata(META_FILE, metadata)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
