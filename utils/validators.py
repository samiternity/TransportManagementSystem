def is_non_empty_string(value: str) -> bool:
    return isinstance(value, str) and value.strip() != ''
