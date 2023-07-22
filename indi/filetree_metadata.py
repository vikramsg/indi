from typing import Any, Dict, List

from loguru import logger
from pydantic import ValidationError

from indi.model import FileTreeMetadata, Metadata, ObjectKey


class ExtractFileTreeMetadata:
    def __init__(self) -> None:
        self.object_keys: List[ObjectKey] = []

        self.sample_id_to_metadata: Dict[str, Metadata] = {}

    def read_json(self, object_keys: Any) -> None:
        if len(object_keys) == 0:
            raise ValueError("Empty list")

        unique_object_keys: Dict[str, int] = {}

        for it, object_key in enumerate(object_keys):
            if object_key in unique_object_keys:
                logger.error(
                    f"Object key {object_key} found on line {it} already exists on line unique_object_keys[object_key]."
                    "Skipping."
                )
            else:
                unique_object_keys[object_key] = it
                self.object_keys.append(ObjectKey(object_key=object_key))

    def extract_filetree_metadata(self) -> None:
        for object_key in self.object_keys:
            try:
                object_key_metadata = Metadata.parse_object_key(object_key)
            except ValidationError as err:
                logger.error(
                    f"Error for object key: {object_key}. Error: {err}. Skipping."
                )

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
