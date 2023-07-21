import pytest
from pydantic import ValidationError

from src.model import Lane, Metadata, ObjectKey
from src.parse_object_key import create_metadata_model_for_object_key, parse_object_key


@pytest.mark.parametrize(
    "object_key_str",
    [
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz"
        ),
    ],
)
def test_object_key_valid(object_key_str: str) -> None:
    # Given

    # When
    object_key = parse_object_key(object_key_str)

    # Then
    assert object_key.object_key == object_key_str


@pytest.mark.parametrize(
    "object_key_str, expected_err_msg",
    [
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Ts13_GAAGGAAG-ATGACGTC_L001_R1_001",
            "Invalid object key. Should end with .fastq.gz",
        ),
        (
            "X123-Tn13wgs/XXBRCDXXX_DNA_X123-Ts13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Must contain 2 /",
        ),
        (
            "X123Tn13/wgs/XXBRCDXXX_DNA_X123-Ts13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Must contain 3 -",
        ),
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Ts13GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Must contain 6 _",
        ),
    ],
)
def test_object_key_invalid(object_key_str: str, expected_err_msg: str) -> None:
    # Given

    # When
    with pytest.raises(ValidationError) as err:
        _ = parse_object_key(object_key_str)

    # Then
    assert any(expected_err_msg in error["msg"] for error in err.value.errors())


@pytest.mark.parametrize(
    "object_key_str, expected_metadata_model",
    [
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            Metadata(
                case_id="X123",
                sample_label="Tn13",
                sample_id="X123-Tn13",
                data_type="wgs",
                lanes=[
                    Lane(
                        path="X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
                        lane=1,
                        marker_forward="GAAGGAAG",
                        marker_reverse="ATGACGTC",
                        barcode="XXBRCDXXX",
                    )
                ],
            ),
        ),
    ],
)
def test_object_key_valid_metadata(
    object_key_str: str, expected_metadata_model: Metadata
) -> None:
    # Given
    object_key = ObjectKey(object_key=object_key_str)

    # When
    object_key_metadata = create_metadata_model_for_object_key(object_key)

    # Then
    assert object_key_metadata == expected_metadata_model
