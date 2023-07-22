import json
from pathlib import Path
from typing import Any

import click
from loguru import logger

from indi.wgs_filetree_metadata import ExtractWGSFileTreeMetadata


def _validate_parent_dir_exists(ctx: Any, param: Any, value: str) -> str:
    output_file_path = Path(value)
    if not output_file_path.parent.exists():
        raise click.BadParameter(
            f"Parent directory of {value} does not exist."
            "Create one or input a location which already has an existing parent directory."
        )
    return value


@click.command()
@click.option(
    "--input-file",
    type=click.Path(exists=True),
    help="Filename for input json",
    required=True,
)
@click.option(
    "--output-file",
    type=click.Path(),
    callback=_validate_parent_dir_exists,
    help="Filename for output json",
    required=True,
)
def main(input_file: str, output_file: str) -> None:
    logger.info("Create ExtractFileTreeMetadata instance.")
    filetree_metadata_extractor = ExtractWGSFileTreeMetadata()

    logger.info("Read input json file.")
    with open(input_file) as op:
        filetree_metadata_extractor.read_json(json.load(op))

    logger.info("Extract metadata from object keys.")
    filetree_metadata_extractor.extract_wgs_filetree_metadata()

    logger.info("Get Filetree Metadata.")
    output_metadata = filetree_metadata_extractor.get_wgs_filetree_metadata()

    logger.info("Write Filetree Metadata to output file.")
    with open(output_file, "w") as fp:
        json.dump(output_metadata, fp, indent=4)


if __name__ == "__main__":
    main()
