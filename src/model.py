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
    def validate_object_key(cls, object_key: str) -> str:
        if not object_key.endswith(".fastq.gz"):
            raise ValueError("Invalid object key. Should end with .fastq.gz")

        return object_key
