import pytest
from src.parse_object_key import parse_object_key
from pydantic import ValidationError


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
    "object_key_str",
    [
        ("X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Ts13_GAAGGAAG-ATGACGTC_L001_R1_001"),
    ],
)
def test_object_key_invalid(object_key_str: str) -> None:
    # Given

    # When
    with pytest.raises(ValidationError) as err:
        _ = parse_object_key(object_key_str)

    # Then
    assert any(
        "Invalid object key. Should end with .fastq.gz" in error["msg"]
        for error in err.value.errors()
    )
