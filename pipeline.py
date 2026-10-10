"""
Data Processing Pipeline - CLI Template

DS 3500 - MP1

Usage:
    python pipeline.py --input fixtures/sample.csv --output cleaned_data.csv --config config.yaml --verbose
"""

import argparse
import logging
import sys
from pathlib import Path
from data_loaders import load_data
from data_processor import process_data, create_cleaning_report

logger = logging.getLogger(__name__)


def setup_logging(verbose=False):
    """Configure logging for the pipeline."""

    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )


def parse_arguments():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Data Processing Pipeline"
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input file"
    )

    parser.add_argument(
    "--config",
    required=True,
    help="Path to a YAML configuration file"
    )

    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to the output file"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def validate_input(filepath):
    """Check whether the input path exists and is a file."""

    if Path(filepath).is_file():
        logger.info(f"Input file validated: {filepath}")
        return True
    else:
        logger.error(f"Input file not found: {filepath}")
        return False


def main():
    """Main pipeline function."""
    args = parse_arguments()

    setup_logging(args.verbose)

    logger.debug(
        f"Arguments parsed: input={args.input}, "
        f"output={args.output}, config={args.config}"
    )

    if not validate_input(args.input):
        sys.exit(1)

    if not validate_input(args.config):
        sys.exit(1)

    try:
        data = load_data(args.input)
        config = load_data(args.config)
    except ValueError as error:
        logger.error("Could not load input or config: %s", error)
        sys.exit(1)

    df_before = data.copy()

    try:
        data = process_data(data, config)
    except ValueError as error:
        logger.error("Could not process data: %s", error)
        sys.exit(1)

    report = create_cleaning_report(df_before, data)

    logger.info(
        "Processing complete: %s → %s rows",
        len(df_before),
        len(data),
    )

    data.to_csv(args.output, index=False)
    logger.info("Saved cleaned data to %s", args.output)

    print(report)
    

if __name__ == "__main__":
    main()