from typing import List

from pydantic import BaseModel, validator


def _snake_to_kebab(snake_str: str) -> str:
    return snake_str.replace("_", "-")


def _dict_encoder(snake_dict: dict) -> dict:
    return {_snake_to_kebab(key): value for key, value in snake_dict.items()}


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

    @classmethod
    def parse_object_key(cls, object_key: str) -> "Metadata":
        # ToDo: Rename
        parts = object_key.split("/")
        case_id, sample_label = parts[0].split("-")
        data_type = parts[1]

        other_parts = parts[2].split("_")
        barcode = other_parts[0]
        lane = int(other_parts[-3][1:])
        marker_forward, marker_reverse = other_parts[3].split("-")

        path = object_key

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

    # ToDo: Write validator for path and sample_id matching

    # JSON output will have kebab case
    class Config:
        json_encoders = {dict: _dict_encoder}


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
