from src.model import Metadata, ObjectKey


def parse_object_key(object_key_str: str) -> ObjectKey:
    object_key = ObjectKey(object_key=object_key_str)

    return object_key


def create_metadata_model_for_object_key(object_key: ObjectKey) -> Metadata:
    object_key_str = object_key.object_key

    return Metadata.parse_object_key(object_key_str)
