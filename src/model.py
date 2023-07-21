from typing import List
from pydantic import BaseModel, validator


class Lane(BaseModel):
    path: str
    lane: int
    marker_forward: str
    marker_reverse: str
    barcode: str


class Metadata(BaseModel):
    case_id: str
    sample_label: str
    sample_id: str
    data_type: str
    lanes: List[Lane]


class ObjectKey(BaseModel):
    object_key: str

    @validator("object_key")
    def validate_object_key(cls, value: str) -> str:
        if not value.endswith(".fastq.gz"):
            raise ValueError("Invalid object key. Should end with .fastq.gz")

        if value.count("/") != 2:
            raise ValueError("Invalid object key. Must contain 2 /")

        if value.count("-") != 3:
            raise ValueError("Invalid object key. Must contain 3 -")

        if value.count("_") != 6:
            raise ValueError("Invalid object key. Must contain 6 _")

        return value
