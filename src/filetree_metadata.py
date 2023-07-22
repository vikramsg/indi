from typing import Any, Dict
from src.model import Metadata, ObjectKey, FileTreeMetadata


def create_metadata_model_for_object_key(object_key: ObjectKey) -> Metadata:
    object_key_str = object_key.object_key

    return Metadata.parse_object_key(object_key_str)


# FIXME: Is Any the correct type?
def extract_file_tree_metadata(input_json: Any) -> Any:
    filetree_metadata = []
    for line in input_json:
        object_key = ObjectKey(object_key=line)

        filetree_metadata.append(create_metadata_model_for_object_key(object_key))

    return FileTreeMetadata(filetree_metadata=filetree_metadata).model_dump()[
        "filetree_metadata"
    ]


class ExtractFileTreeMetadata:
    def __init__(self) -> None:
        self.object_keys = None

        self.sample_id_to_metadata = {}

        self.filetree_metadata = None

    def read_json(self, object_keys: Dict[str, Any]) -> None:
        if len(object_keys) == 0:
            raise ValueError("Empty list")

        # Convert to ObjectKey which will do first level of validation
        self.object_keys = [ObjectKey[object_key] for object_key in object_keys]

    def extract_file_tree_metadata(self) -> None:
        for object_key in self.object_keys:
            object_key_metadata = Metadata.parse_object_key(object_key)
