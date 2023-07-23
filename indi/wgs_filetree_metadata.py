from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import ValidationError

from indi.model import WGSFileTreeMetadata, WGSMetadata, WGSObjectKey


class ExtractWGSFileTreeMetadata:
    def __init__(self) -> None:
        # List of all valid objects keys
        self.object_keys: List[WGSObjectKey] = []

        self.wgs_filetree_metadata: Optional[WGSFileTreeMetadata] = None

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

    def _get_combined_metadata_for_sample_id(
        self, object_keys: List[WGSObjectKey]
    ) -> List[WGSMetadata]:
        """
        Combining metadata from object keys to make sure
        1 sample_id has 1 Metadata object
        """

        # Dictionary to use for ensuring 1 sample_id has only 1 WGSMetadata object
        sample_id_to_metadata: Dict[str, WGSMetadata] = {}

        for object_key in object_keys:
            object_key_metadata = self._object_key_to_metadata(object_key)
            if object_key_metadata is None:
                continue

            sample_id = object_key_metadata.sample_id
            if sample_id not in sample_id_to_metadata:
                sample_id_to_metadata[sample_id] = object_key_metadata
            else:
                sample_id_to_metadata[sample_id].lanes.extend(object_key_metadata.lanes)

        return list(sample_id_to_metadata.values())

    def _sort_metadata_lanes(
        self, sample_id_metadata: List[WGSMetadata]
    ) -> List[WGSMetadata]:
        """
        Sort lanes in metadata for better readability
        """
        wgs_filetree_metadata: List[WGSMetadata] = []
        for metadata in sample_id_metadata:
            lanes = sorted(
                metadata.lanes,
                key=lambda lane: (
                    lane.barcode,
                    lane.marker_forward,
                    lane.marker_reverse,
                    lane.lane,
                ),
            )

            wgs_filetree_metadata.append(
                WGSMetadata(
                    case_id=metadata.case_id,
                    sample_label=metadata.sample_label,
                    sample_id=metadata.sample_id,
                    data_type=metadata.data_type,
                    lanes=lanes,
                )
            )
        return wgs_filetree_metadata

    def extract_wgs_filetree_metadata(self) -> None:
        """
        This is an orchestrator function to extract WGS metadata from the object keys.
        First we make sure to use only unique keys.
        Then, we convert object keys to metadata.
        Then, we combine metadata to make sure 1 sample_id has 1 Metadata object.
        Finally, we sort lanes for metadata for better readability.
        """
        object_keys = self._unique_object_keys()

        # Dictionary to use for ensuring 1 sample_id has only 1 WGSMetadata object
        sample_id_metadata = self._get_combined_metadata_for_sample_id(object_keys)

        wgs_filetree_metadata = self._sort_metadata_lanes(sample_id_metadata)

        self.wgs_filetree_metadata = WGSFileTreeMetadata(
            filetree_metadata=wgs_filetree_metadata
        )

    def get_wgs_filetree_metadata(self) -> Any:
        """Create json from the metadata ensuring correct names

        Returns:
            Any: json for the metadata

        Raises:
            ValueError: Raise error if metadata is None
        """
        if self.wgs_filetree_metadata is not None:
            return self.wgs_filetree_metadata.model_dump(by_alias=True)[
                "filetree_metadata"
            ]
        else:
            raise ValueError("Filetree is None. Process it before getting data.")
