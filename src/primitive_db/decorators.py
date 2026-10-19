import time


def handle_db_errors(func):
    """Перехватывает ошибки БД (KeyError, ValueError, FileNotFoundError)."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(f"Ошибка: Нет такого ключа — {e}")
            return args[0] if args else None
        except ValueError as e:
            print(f"Ошибка значения: {e}")
            return args[0] if args else None
        except FileNotFoundError:
            print("Ошибка: Файл не найден")
            return args[0] if args else None
    return wrapper

def confirm_action(action_name):
    """Запрашивает подтверждение пользователя перед опасной операцией."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func):
    """Замеряет и выводит время выполнения функции."""
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд")
        return result
    return wrapper

def create_cacher():
    """Возвращает функцию-кэшер для запоминания результатов."""
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result