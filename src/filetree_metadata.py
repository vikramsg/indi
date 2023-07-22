from typing import Any, Dict, List

from src.model import FileTreeMetadata, Metadata, ObjectKey


class ExtractFileTreeMetadata:
    def __init__(self) -> None:
        self.object_keys: List[ObjectKey] = []

        self.sample_id_to_metadata: Dict[str, Metadata] = {}

    def read_json(self, object_keys: Dict[str, Any]) -> None:
        if len(object_keys) == 0:
            raise ValueError("Empty list")

        # Convert to ObjectKey which will do first level of validation
        self.object_keys = [
            ObjectKey(object_key=object_key) for object_key in object_keys
        ]

    def extract_filetree_metadata(self) -> None:
        for object_key in self.object_keys:
            object_key_metadata = Metadata.parse_object_key(object_key)

            sample_id = object_key_metadata.sample_id
            if sample_id not in self.sample_id_to_metadata:
                self.sample_id_to_metadata[sample_id] = object_key_metadata
            else:
                self.sample_id_to_metadata[sample_id].lanes.extend(
                    object_key_metadata.lanes
                )

    def get_filetree_metadata(self) -> Any:
        return FileTreeMetadata(
            filetree_metadata=list(self.sample_id_to_metadata.values())
        ).model_dump(by_alias=True)["filetree_metadata"]
