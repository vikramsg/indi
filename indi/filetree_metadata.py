from typing import Any, Dict, List, Optional

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

        for object_key in object_keys:
            self.object_keys.append(ObjectKey(object_key=object_key))

    def _unique_object_keys(self) -> List[ObjectKey]:
        unique_object_keys = []
        object_key_dict: Dict[str, int] = {}
        for it, object_key in enumerate(self.object_keys):
            if object_key.object_key in object_key_dict:
                logger.error(
                    f"Object key {object_key.object_key} found on line {it} "
                    f"already exists on line {object_key_dict[object_key.object_key]}."
                    "Skipping."
                )
            else:
                object_key_dict[object_key.object_key] = it
                unique_object_keys.append(object_key)

        return unique_object_keys

    def _parse_object_key(self, object_key: ObjectKey) -> Optional[Metadata]:
        try:
            return Metadata.parse_object_key(object_key)
        except ValidationError as err:
            logger.error(
                f"Error for object key: {object_key}. Error: {err}.\nSkipping."
            )
            return None

    def extract_filetree_metadata(self) -> None:
        object_keys = self._unique_object_keys()
        for object_key in object_keys:
            object_key_metadata = self._parse_object_key(object_key)
            if not object_key_metadata:
                continue

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
