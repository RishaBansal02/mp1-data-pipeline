import logging

import pandas as pd

logger = logging.getLogger(__name__)


def validate_dataframe(df, required_columns, numeric_columns):
    """Check required columns and convert configured numeric columns."""
    rows_before = len(df)

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]
    if missing_columns:
        message = f"Required columns not found: {missing_columns}"
        logger.error(message)
        raise ValueError(message)

    df = df.copy()

    for column in numeric_columns:
        invalid_rows = []

        for index, value in df[column].items():
            if pd.notna(value):
                try:
                    float(value)
                except (ValueError, TypeError):
                    invalid_rows.append(index)

        if invalid_rows:
            logger.warning(
                "Removed %s rows with invalid numeric values in %s",
                len(invalid_rows),
                column,
            )
            df = df.drop(index=invalid_rows)

        df[column] = pd.to_numeric(df[column])

    logger.debug("Validation: %s -> %s rows", rows_before, len(df))
    return df