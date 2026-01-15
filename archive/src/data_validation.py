"""
Data Validation Module

Validates input CSV files and configuration data for portfolio analysis.
"""

import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def validate_holdings_csv(filepath):
    """
    Validate holdings.csv file format.

    Expected columns: ticker, quantity, avg_cost

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        if not Path(filepath).exists():
            return False, f"File not found: {filepath}"

        df = pd.read_csv(filepath)

        # Check required columns
        required_columns = ["ticker", "quantity", "avg_cost"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"

        # Validate data types
        if not pd.api.types.is_numeric_dtype(df["quantity"]):
            return False, "Column 'quantity' must contain numeric values"

        if not pd.api.types.is_numeric_dtype(df["avg_cost"]):
            return False, "Column 'avg_cost' must contain numeric values"

        # Check for negative values
        if (df["quantity"] < 0).any():
            return False, "Column 'quantity' contains negative values"

        if (df["avg_cost"] < 0).any():
            return False, "Column 'avg_cost' contains negative values"

        # Validate ticker symbols (basic check)
        if df["ticker"].isnull().any():
            return False, "Column 'ticker' contains null values"

        if not df["ticker"].astype(str).str.match(r"^[A-Z0-9\.\-]+$").all():
            invalid_tickers = df[
                ~df["ticker"].astype(str).str.match(r"^[A-Z0-9\.\-]+$")
            ]["ticker"].tolist()
            return (
                False,
                f"Invalid ticker symbols: {', '.join(map(str, invalid_tickers))}",
            )

        logger.info(f"Holdings CSV validated successfully: {len(df)} positions")
        return True, None

    except pd.errors.EmptyDataError:
        return False, "CSV file is empty"
    except pd.errors.ParserError as e:
        return False, f"CSV parsing error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error validating holdings CSV: {e}", exc_info=True)
        return False, f"Validation error: {e}"


def validate_targets_csv(filepath):
    """
    Validate targets.csv file format.

    Expected columns: ticker, target_pct (or target_value)

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        if not Path(filepath).exists():
            return False, f"File not found: {filepath}"

        df = pd.read_csv(filepath)

        # Check required columns
        if "ticker" not in df.columns:
            return False, "Missing required column: 'ticker'"

        # Must have either target_pct or target_value
        has_target_pct = "target_pct" in df.columns
        has_target_value = "target_value" in df.columns

        if not (has_target_pct or has_target_value):
            return False, "Must have either 'target_pct' or 'target_value' column"

        # Validate numeric columns
        if has_target_pct:
            if not pd.api.types.is_numeric_dtype(df["target_pct"]):
                return False, "Column 'target_pct' must contain numeric values"

            if (df["target_pct"] < 0).any() or (df["target_pct"] > 100).any():
                return False, "Column 'target_pct' must be between 0 and 100"

        if has_target_value:
            if not pd.api.types.is_numeric_dtype(df["target_value"]):
                return False, "Column 'target_value' must contain numeric values"

            if (df["target_value"] < 0).any():
                return False, "Column 'target_value' contains negative values"

        # Validate ticker symbols
        if df["ticker"].isnull().any():
            return False, "Column 'ticker' contains null values"

        logger.info(f"Targets CSV validated successfully: {len(df)} targets")
        return True, None

    except pd.errors.EmptyDataError:
        return False, "CSV file is empty"
    except pd.errors.ParserError as e:
        return False, f"CSV parsing error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error validating targets CSV: {e}", exc_info=True)
        return False, f"Validation error: {e}"


def validate_stocks_txt(filepath):
    """
    Validate stocks.txt file format.

    Expected format: One ticker per line, or basket format: [Basket Name] TICK1, TICK2

    Returns:
        tuple: (is_valid: bool, error_message: str or None, ticker_count: int)
    """
    try:
        if not Path(filepath).exists():
            return False, f"File not found: {filepath}", 0

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return False, "File is empty", 0

        ticker_count = 0
        line_num = 0

        for line in lines:
            line_num += 1
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Check basket format: [Basket Name] TICK1, TICK2
            if line.startswith("["):
                if "]" not in line:
                    return (
                        False,
                        f"Line {line_num}: Invalid basket format (missing closing bracket)",
                        ticker_count,
                    )

                bracket_end = line.index("]")
                basket_name = line[1:bracket_end].strip()

                if not basket_name:
                    return False, f"Line {line_num}: Empty basket name", ticker_count

                tickers_str = line[bracket_end + 1 :].strip()
                if not tickers_str:
                    return (
                        False,
                        f"Line {line_num}: No tickers in basket '{basket_name}'",
                        ticker_count,
                    )

                tickers = [t.strip().upper() for t in tickers_str.split(",")]
                ticker_count += len(tickers)
            else:
                # Individual ticker - basic validation
                ticker = line.upper()
                if not ticker.replace("-", "").replace(".", "").isalnum():
                    return (
                        False,
                        f"Line {line_num}: Invalid ticker symbol '{ticker}'",
                        ticker_count,
                    )
                ticker_count += 1

        if ticker_count == 0:
            return False, "No valid tickers found in file", 0

        logger.info(f"Stocks file validated successfully: {ticker_count} tickers")
        return True, None, ticker_count

    except Exception as e:
        logger.error(f"Unexpected error validating stocks.txt: {e}", exc_info=True)
        return False, f"Validation error: {e}", 0
