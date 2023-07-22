from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator


class WGSObjectKey(BaseModel):
    object_key: str

    @field_validator("object_key")
    def validate_object_key(cls, value: str) -> str:
        if len(value) == 0:
            raise ValueError("Invalid object key. Should not be empty.")

        if not value.endswith(".fastq.gz"):
            raise ValueError("Invalid object key. Should end with .fastq.gz")

        if value.count("/") != 2:
            raise ValueError("Invalid object key. Must contain 2 /")

        if value.count("-") != 3:
            raise ValueError("Invalid object key. Must contain 3 -")

        if value.count("_") != 6:
            raise ValueError("Invalid object key. Must contain 6 _")

        return value


class Lane(BaseModel):
    path: str
    lane: int
    marker_forward: str = Field(serialization_alias="marker-forward")
    marker_reverse: str = Field(serialization_alias="marker-reverse")
    barcode: str


class WGSMetadata(BaseModel):
    case_id: str = Field(serialization_alias="case-id")
    sample_label: str = Field(serialization_alias="sample-label")
    sample_id: str = Field(serialization_alias="sample-id")
    data_type: str = Field(serialization_alias="data-type")
    lanes: List[Lane]

    @classmethod
    def parse_object_key(cls, object_key: WGSObjectKey) -> "WGSMetadata":
        """
        Create Metadata for a single object key
        """
        object_key_str = object_key.object_key
        slash_split_parts = object_key_str.split("/")
        case_id, sample_label = slash_split_parts[0].split("-")
        data_type = slash_split_parts[1]

        underscore_split_parts = slash_split_parts[2].split("_")
        barcode = underscore_split_parts[0]
        lane = int(underscore_split_parts[-3][1:])
        marker_forward, marker_reverse = underscore_split_parts[3].split("-")

        path = object_key_str

        return cls(
            case_id=case_id,
            sample_label=sample_label,
            sample_id=f"{case_id}-{sample_label}",
            data_type=data_type,
            lanes=[
                Lane(
                    path=path,
                    lane=lane,
                    marker_forward=marker_forward,
                    marker_reverse=marker_reverse,
                    barcode=barcode,
                )
            ],
        )

    @model_validator(mode="after")
    def validate_path_matches_sample_id(self) -> "WGSMetadata":
        if self.sample_id != self.lanes[0].path.split("/")[2].split("_")[2]:
            raise ValueError(
                """Invalid object key. The same sample id must be present at the beginning and in the middle,
                that is, the path must be <sample_id/data_type/..._sample_id_....>"""
            )

        return self


class WGSFileTreeMetadata(BaseModel):
    filetree_metadata: List[WGSMetadata]
