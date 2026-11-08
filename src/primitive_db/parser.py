def convert_value(text):
    """Преобразует строку в значение нужного типа: str, bool или int."""
    text = text.strip()
    if len(text) >= 2 and text[0] in "\"'" and text[-1] == text[0]:
        return text[1:-1]
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(text)
    except ValueError:
        return None


def parse_values(raw_values):
    """Разбирает строку вида "(v1, v2, ...)" в список значений."""
    raw = raw_values.strip()
    if not raw.startswith("(") or not raw.endswith(")"):
        return None
    inner = raw[1:-1].strip()
    if not inner:
        return []
    values = []
    for part in inner.split(","):
        value = convert_value(part)
        if value is None:
            return None
        values.append(value)
    return values


def parse_where(condition):
    """Разбирает строку "столбец = значение" в словарь {"столбец": значение}."""
    column, sep, raw_value = condition.partition("=")
    if not sep or not column.strip():
        return None
    value = convert_value(raw_value)
    if value is None:
        return None
    return {column.strip(): value}
