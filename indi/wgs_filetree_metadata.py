from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import ValidationError

from indi.model import WGSFileTreeMetadata, WGSMetadata, WGSObjectKey


class ExtractWGSFileTreeMetadata:
    def __init__(self) -> None:
        # List of all valid objects keys
        self.object_keys: List[WGSObjectKey] = []

        # Dictionary to use for ensuring 1 sample_id has only 1 WGSMetadata object
        self.sample_id_to_metadata: Dict[str, WGSMetadata] = {}

    def read_json(self, object_keys: Any) -> None:
        """Read in the list of object keys,
        convert each to WGSObjectKey object for validation and store in a list

        Args:
            object_keys (Any): List of object keys

        Raises:
            ValueError: Raise error if the input is empty
        """
        if not object_keys:
            raise ValueError("Empty list")

        for object_key in object_keys:
            try:
                self.object_keys.append(WGSObjectKey(object_key=object_key))
            except ValidationError as err:
                logger.error(
                    f"""Error for object key: {object_key}.\nError: {err.errors()[0]["msg"]}\nSkipping."""
                )

    def _unique_object_keys(self) -> List[WGSObjectKey]:
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

    def _object_key_to_metadata(
        self, object_key: WGSObjectKey
    ) -> Optional[WGSMetadata]:
        try:
            return WGSMetadata.parse_object_key(object_key)
        except ValidationError as err:
            logger.error(
                f"""Error for object key: {object_key}.\nError: {err.errors()[0]["msg"]}\nSkipping."""
            )
            return None

    def extract_wgs_filetree_metadata(self) -> None:
        """
        Create WGS metadata from the object keys.
        First we make sure to use only unique keys.
        Then, we convert object keys to metadata, and make sure it is valid
        Then, for all metadata that already have sample_ids
        we extract the lane and append it to the unique sample_id metadata
        """
        object_keys = self._unique_object_keys()

        for object_key in object_keys:
            object_key_metadata = self._object_key_to_metadata(object_key)
            if object_key_metadata is None:
                continue

            sample_id = object_key_metadata.sample_id
            if sample_id not in self.sample_id_to_metadata:
                self.sample_id_to_metadata[sample_id] = object_key_metadata
            else:
                self.sample_id_to_metadata[sample_id].lanes.extend(
                    object_key_metadata.lanes
                )

    def get_wgs_filetree_metadata(self) -> Any:
        """Create json from the metadata ensuring correct names

        Returns:
            Any: json for the metadata
        """
        return WGSFileTreeMetadata(
            filetree_metadata=list(self.sample_id_to_metadata.values())
        ).model_dump(by_alias=True)["filetree_metadata"]
