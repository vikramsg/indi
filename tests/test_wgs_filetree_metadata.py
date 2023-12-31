import json

import pytest
from pydantic import ValidationError

from indi.model import Lane, WGSMetadata, WGSObjectKey
from indi.wgs_filetree_metadata import ExtractWGSFileTreeMetadata


@pytest.mark.parametrize(
    "object_key_str",
    [
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz"
        ),
    ],
)
def test_object_key_valid(object_key_str: str) -> None:
    # When
    object_key = WGSObjectKey(object_key=object_key_str)

    # Then
    assert object_key.object_key == object_key_str


@pytest.mark.parametrize(
    "object_key_str, expected_err_msg",
    [
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001",
            "Invalid object key. Should end with .fastq.gz",
        ),
        (
            "X123-Tn13wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Must contain 2 /",
        ),
        (
            "X123Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Must contain 3 -",
        ),
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Must contain 6 _",
        ),
        (
            "X123-Tn13/wg2/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Data type must be wgs.",
        ),
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Ts13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. The same sample id must be present at the beginning and in the middle.",
        ),
        (
            "X123-Tn13/wgs/XXBRCDXXX_RNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            "Invalid object key. Object key must have DNA at the second position in path.",
        ),
    ],
)
def test_object_key_invalid(object_key_str: str, expected_err_msg: str) -> None:
    # When
    with pytest.raises(ValidationError) as err:
        _ = WGSObjectKey(object_key=object_key_str)

    # Then
    assert any(expected_err_msg in error["msg"] for error in err.value.errors())


@pytest.mark.parametrize(
    "object_key_str, expected_metadata_model",
    [
        (
            "X123-Tn13/wgs/XXBRCDXXX_DNA_X123-Tn13_GAAGGAAG-ATGACGTC_L001_R1_001.fastq.gz",
            WGSMetadata(
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
    object_key_str: str, expected_metadata_model: WGSMetadata
) -> None:
    # Given
    object_key = WGSObjectKey(object_key=object_key_str)

    # When
    object_key_metadata = WGSMetadata.parse_object_key(object_key)

    # Then
    assert object_key_metadata == expected_metadata_model


def test_extract_filetree_metadata_with_valid_keys_only(
    filetree_input_json: str, filetree_expected_output_json: str
) -> None:
    # Given
    input_object_keys = json.loads(filetree_input_json)
    expected_output_metadata = json.loads(filetree_expected_output_json)

    metadata_extractor = ExtractWGSFileTreeMetadata()
    metadata_extractor.read_json(input_object_keys)

    # When
    metadata_extractor.extract_wgs_filetree_metadata()
    output_metadata = metadata_extractor.get_wgs_filetree_metadata()

    # Then
    assert expected_output_metadata == output_metadata


def test_extract_filetree_metadata_with_invalid_keys(
    filetree_input_json_with_invalid_keys: str, filetree_expected_output_json: str
) -> None:
    # Given
    input_object_keys = json.loads(filetree_input_json_with_invalid_keys)
    expected_output_metadata = json.loads(filetree_expected_output_json)

    metadata_extractor = ExtractWGSFileTreeMetadata()
    metadata_extractor.read_json(input_object_keys)

    # When
    metadata_extractor.extract_wgs_filetree_metadata()
    output_metadata = metadata_extractor.get_wgs_filetree_metadata()

    # Then
    assert expected_output_metadata == output_metadata


def test_extract_filetree_metadata_from_identical_keys() -> None:
    # Given
    input_object_keys = json.loads(
        json.dumps(
            [
                "Y512-Tc7/wgs/HWW7GDSXX_DNA_Y512-Tc7_TGAAGACG-TGGCATGA_L002_R1_001.fastq.gz",
                "Y512-Tc7/wgs/HWW7GDSXX_DNA_Y512-Tc7_TGAAGACG-TGGCATGA_L002_R1_001.fastq.gz",
            ]
        )
    )

    metadata_extractor = ExtractWGSFileTreeMetadata()
    metadata_extractor.read_json(input_object_keys)

    # When
    metadata_extractor.extract_wgs_filetree_metadata()
    output_metadata = metadata_extractor.get_wgs_filetree_metadata()

    # Then
    assert output_metadata == [
        {
            "case-id": "Y512",
            "sample-label": "Tc7",
            "sample-id": "Y512-Tc7",
            "data-type": "wgs",
            "lanes": [
                {
                    "path": "Y512-Tc7/wgs/HWW7GDSXX_DNA_Y512-Tc7_TGAAGACG-TGGCATGA_L002_R1_001.fastq.gz",
                    "lane": 2,
                    "marker-forward": "TGAAGACG",
                    "marker-reverse": "TGGCATGA",
                    "barcode": "HWW7GDSXX",
                },
            ],
        },
    ]


@pytest.fixture
def filetree_input_json() -> str:
    return json.dumps(
        [
            "X123-Tp2/wgs/HWYLNDSXX_DNA_X123-Tp2_GAAGGAAG-ATGACGTC_L003_R1_001.fastq.gz",
            "X123-Tp2/wgs/HWYLNDSXX_DNA_X123-Tp2_GAAGGAAG-ATGACGTC_L004_R1_001.fastq.gz",
            "X121-Tn16/wgs/HYKKLDSXX_DNA_X121-Tn16_GTTGTTCG-GAAGTTGG_L001_R1_001.fastq.gz",
            "X121-Tn16/wgs/HYKKLDSXX_DNA_X121-Tn16_GTTGTTCG-GAAGTTGG_L002_R1_001.fastq.gz",
        ]
    )


@pytest.fixture
def filetree_input_json_with_invalid_keys() -> str:
    return json.dumps(
        [
            "X123-Tp2/wgs/HWYLNDSXX_DNA_X123-Tp2_GAAGGAAG-ATGACGTC_L003_R1_001.fastq.gz",
            "X123-Tp2/wgs/HWYLNDSXX_DNA_X123-Tp2_GAAGGAAG-ATGACGTC_L004_R1_001.fastq.gz",
            "X123-Tp2/wgs/HWYLNDSXX_DNA_X123-Tp1_GAAGGAAG-ATGACGTC_L004_R1_001.fastq.gz",
            "X121-Tn16/wgs/HYKKLDSXX_DNA_X121-Tn16_GTTGTTCG-GAAGTTGG_L001_R1_001.fastq.gz",
            "X121-Tn16/wgs/HYKKLDSXX_DNA_X121-Tn16_GTTGTTCG-GAAGTTGG_L002_R1_001.fastq.gz",
            "X121-Tn16/wgs/HYKKLDSXX_DNA_X123-Tn16_GTTGTTCG-GAAGTTGG_L002_R1_001.fastq.gz",
        ]
    )


@pytest.fixture
def filetree_expected_output_json() -> str:
    return json.dumps(
        [
            {
                "case-id": "X123",
                "sample-label": "Tp2",
                "sample-id": "X123-Tp2",
                "data-type": "wgs",
                "lanes": [
                    {
                        "path": "X123-Tp2/wgs/HWYLNDSXX_DNA_X123-Tp2_GAAGGAAG-ATGACGTC_L003_R1_001.fastq.gz",
                        "lane": 3,
                        "marker-forward": "GAAGGAAG",
                        "marker-reverse": "ATGACGTC",
                        "barcode": "HWYLNDSXX",
                    },
                    {
                        "path": "X123-Tp2/wgs/HWYLNDSXX_DNA_X123-Tp2_GAAGGAAG-ATGACGTC_L004_R1_001.fastq.gz",
                        "lane": 4,
                        "marker-forward": "GAAGGAAG",
                        "marker-reverse": "ATGACGTC",
                        "barcode": "HWYLNDSXX",
                    },
                ],
            },
            {
                "case-id": "X121",
                "sample-label": "Tn16",
                "sample-id": "X121-Tn16",
                "data-type": "wgs",
                "lanes": [
                    {
                        "path": "X121-Tn16/wgs/HYKKLDSXX_DNA_X121-Tn16_GTTGTTCG-GAAGTTGG_L001_R1_001.fastq.gz",
                        "lane": 1,
                        "marker-forward": "GTTGTTCG",
                        "marker-reverse": "GAAGTTGG",
                        "barcode": "HYKKLDSXX",
                    },
                    {
                        "path": "X121-Tn16/wgs/HYKKLDSXX_DNA_X121-Tn16_GTTGTTCG-GAAGTTGG_L002_R1_001.fastq.gz",
                        "lane": 2,
                        "marker-forward": "GTTGTTCG",
                        "marker-reverse": "GAAGTTGG",
                        "barcode": "HYKKLDSXX",
                    },
                ],
            },
        ]
    )
