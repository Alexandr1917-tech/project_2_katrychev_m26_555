def convert_value(token):
    """Преобразует строковый токен в int, bool или str."""
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    if token in ("True", "true"):
        return True
    if token in ("False", "false"):
        return False
    return int(token)


def parse_where(tokens):
    """Разбирает условие where в словарь {поле: значение}."""
    return {tokens[0]: convert_value(tokens[2])}


def parse_set(tokens):
    """Разбирает условие set в словарь {поле: значение}."""
    return {tokens[0]: convert_value(tokens[2])}