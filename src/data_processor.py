import logging

import pandas as pd
from pandas.api.types import is_numeric_dtype

logger = logging.getLogger(__name__)


def remove_duplicates(df):
    """Remove duplicate rows."""
    rows_before = len(df)
    result = df.drop_duplicates()
    rows_removed = rows_before - len(result)

    logger.debug("remove_duplicates: removed %s rows", rows_removed)
    return result


def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis == "rows":
        result = df.dropna(axis=0)
        removed = len(df) - len(result)
        logger.debug("handle_missing: removed %s rows", removed)
    elif axis == "columns":
        result = df.dropna(axis=1)
        removed = len(df.columns) - len(result.columns)
        logger.debug("handle_missing: removed %s columns", removed)
    else:
        logger.error("Unsupported missing-value axis: %s", axis)
        raise ValueError(f"Unsupported missing-value axis: {axis}")

    return result


def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    if method not in ("iqr", "zscore"):
        logger.error("Unsupported outlier method: %s", method)
        raise ValueError(f"Unsupported outlier method: {method}")

    result = df.copy()

    for column in columns:
        if column not in result.columns:
            logger.warning("Column not found: %s", column)
            continue

        if not is_numeric_dtype(result[column]):
            logger.warning("Column is not numeric: %s", column)
            continue

        values = result[column]

        if method == "iqr":
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr

            # Keep missing values here; the missing-value step handles them.
            keep_rows = values.between(lower, upper) | values.isna()

            logger.debug(
                "%s: lower=%s, upper=%s",
                column,
                lower,
                upper,
            )
        else:  # method == "zscore"
            standard_deviation = values.std(ddof=0)

            if standard_deviation == 0:
                # A constant column has no outliers by z-score.
                keep_rows = pd.Series(True, index=result.index)
            else:
                z_scores = (values - values.mean()) / standard_deviation
                keep_rows = (z_scores.abs() <= threshold) | values.isna()

        rows_before = len(result)
        result = result.loc[keep_rows]
        rows_removed = rows_before - len(result)

        logger.debug(
            "%s: method=%s, threshold=%s, removed=%s",
            column,
            method,
            threshold,
            rows_removed,
        )

    return result


def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""
    processing = config["processing"]
    result = df

    if processing.get("remove_duplicates", False):
        result = remove_duplicates(result)

    missing_config = processing.get("missing", {})
    if missing_config.get("enabled", False):
        result = handle_missing(
            result,
            axis=missing_config.get("axis", "rows"),
        )

    outlier_config = processing.get("outliers", {})
    if outlier_config.get("enabled", False):
        result = remove_outliers(
            result,
            columns=outlier_config["columns"],
            method=outlier_config["method"],
            threshold=outlier_config["threshold"],
        )

    return result


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before = len(df_before)
    rows_after = len(df_after)
    columns_before = len(df_before.columns)
    columns_after = len(df_after.columns)

    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_before - rows_after,
        "columns_before": columns_before,
        "columns_after": columns_after,
        "columns_removed": columns_before - columns_after,
    }