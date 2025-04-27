import os
import re
import uuid

def is_int_in_range(value: str, min_val: int, max_val: int) -> bool:
    try:
        num = int(value.strip())
        return min_val <= num <= max_val
    except (ValueError, AttributeError):
        return False

def is_float_in_range(value: str, min_val: float, max_val: float) -> bool:
    try:
        num = float(value.strip())
        return min_val < num <= max_val
    except (ValueError, AttributeError):
        return False

def is_boolean(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return value.strip().lower() in ["true", "false", "yes", "no"]

def is_valid_package_type(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return value.strip().lower() in ["rpm", "deb"]

def is_existing_directory(path: str) -> bool:
    if not isinstance(path, str):
        return False
    return os.path.isabs(path.strip()) and os.path.isdir(path.strip())

def is_valid_uuid(value: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        uuid.UUID(value.strip())
        return True
    except (ValueError, AttributeError):
        return False

def is_valid_locale(value: str) -> bool:
    if not isinstance(value, str):
        return False
    pattern = r'^[a-zA-Z]{2}[_-][a-zA-Z]{2}(\.[\w\-]+)?$'
    return bool(re.match(pattern, value.strip()))

def is_valid_timeout_with_m(value: str, min_val: int, max_val: int) -> bool:
    if not isinstance(value, str):
        return False
    value = value.strip()
    if not value.endswith('m'):
        return False
    try:
        num = int(value[:-1])
        return min_val <= num <= max_val
    except (ValueError, AttributeError):
        return False

def is_valid_memory_value(value: str) -> bool:
    if not isinstance(value, str):
        return False
    value = value.strip()
    if value.lower() in ["off", "auto"]:
        return True
    return is_float_in_range(value, 0, 100)