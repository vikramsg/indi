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
        slash_split_parts = object_key.split("/")
        case_id, sample_label = slash_split_parts[0].split("-")
        data_type = slash_split_parts[1]

        underscore_split_parts = slash_split_parts[2].split("_")
        barcode = underscore_split_parts[0]
        lane = int(underscore_split_parts[-3][1:])
        marker_forward, marker_reverse = underscore_split_parts[3].split("-")

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

    @validator("lanes")
    def validate_path_matches_sample_id(cls, lanes, values):
        if values["sample_id"] != lanes[0].path.split("/")[2].split("_")[2]:
            raise ValueError(
                """Invalid object key. The same sample id must be present at the beginning and in the middle,
                that is, the path must be <sample_id/data_type/..._sample_id_....>"""
            )

        return lanes

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
