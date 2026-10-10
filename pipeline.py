"""
Data Processing Pipeline - CLI

Usage:
    python pipeline.py --input fixtures/sample_data.csv \
        --output output/clean.csv \
        --config config/config.yaml --verbose
"""

import argparse
import logging
import sys

from src import (
    create_cleaning_report,
    load_data,
    process_data,
    save_data,
    setup_logging,
    validate_dataframe,
    validate_input,
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Data Processing Pipeline"
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input file",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to a YAML configuration file",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to the output file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main():
    """Run the complete data processing pipeline."""
    args = parse_arguments()
    setup_logging(args.verbose)

    logger.debug(
        "Arguments parsed: input=%s, output=%s, config=%s",
        args.input,
        args.output,
        args.config,
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

    validation_config = config.get("validation", {})
    required_columns = validation_config.get("required_columns", [])
    numeric_columns = validation_config.get("numeric_columns", [])

    rows_before_validation = len(data)

    try:
        data = validate_dataframe(data, required_columns, numeric_columns)
    except ValueError as error:
        logger.error("Could not validate data: %s", error)
        sys.exit(1)

    logger.info(
        "Validation complete: %s -> %s rows",
        rows_before_validation,
        len(data),
    )

    df_before = data.copy()

    try:
        data = process_data(data, config)
    except ValueError as error:
        logger.error("Could not process data: %s", error)
        sys.exit(1)

    report = create_cleaning_report(df_before, data)

    logger.info(
        "Processing complete: %s -> %s rows",
        len(df_before),
        len(data),
    )

    save_data(data, args.output)
    logger.info("Saved cleaned data to %s", args.output)

    print("Cleaning report:")
    print(report)


if __name__ == "__main__":
    main()