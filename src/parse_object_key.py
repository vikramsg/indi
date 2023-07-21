from src.model import ObjectKey


def parse_object_key(object_key_str: str) -> ObjectKey:
    object_key = ObjectKey(object_key=object_key_str)

    return object_key
