import functools
import time

import prompt


def handle_db_errors(func):
    """Перехватывает исключения и выводит понятные сообщения об ошибках."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден."
                " Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед выполнением опасной операции."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = prompt.string(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Замеряет и выводит время выполнения функции."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")
        return result


    return wrapper


def create_cacher():
    """Создаёт функцию кэширования результатов по ключу (замыкание)."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает значение из кэша или вычисляет и сохраняет его."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
