import json
from pathlib import Path

import click
from loguru import logger

from indi.filetree_metadata import ExtractFileTreeMetadata


@click.command()
@click.option(
    "--input-file",
    type=click.Path(exists=True),
    help="Filename for input json",
    required=True,
)
@click.option(
    "--output-file",
    type=click.Path(exists=True),
    help="Filename for output json",
    required=True,
)
def main(input_file: str, output_file: str) -> None:
    logger.info("Create ExtractFileTreeMetadata instance.")
    filetree_metadata_extractor = ExtractFileTreeMetadata()

    logger.info("Read input json file.")
    with open(input_file) as op:
        filetree_metadata_extractor.read_json(json.load(op))

    logger.info("Extract metadata from object keys.")
    filetree_metadata_extractor.extract_filetree_metadata()

    logger.info("Get Filetree Metadata.")
    output_metadata = filetree_metadata_extractor.get_filetree_metadata()

    logger.info("Get Filetree Metadata.")
    with open(output_file, "w") as fp:
        json.dump(output_metadata, fp)


if __name__ == "__main__":
    main()
