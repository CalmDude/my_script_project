# Example Scripts

Development and debugging scripts that demonstrate specific features.

## Historical Data Testing

### `test_historical_price.py`
Verifies historical price fetching functionality.

**Purpose:** Tests that `as_of_date` parameter properly limits data to historical dates.

**Tests:**
- QCOM on 2024-01-01 (expected ~$142)
- AAPL on 2024-01-01 (expected ~$185)
- MSFT on 2023-06-15 (expected ~$334)

**Usage:**
```bash
python scripts/examples/test_historical_price.py
```

---

### `test_historical_scan.py`
Quick test of historical scanning functionality.

**Purpose:** Validates that scanner can analyze stocks as of a past date.

**Tests:**
- Scans AAPL, MSFT, GOOGL on 2025-07-01
- Uses `as_of_date` parameter in `scan_stocks()`

**Usage:**
```bash
python scripts/examples/test_historical_scan.py
```

---

### `test_qcom_details.py`
Shows complete technical analysis details for QCOM on a historical date.

**Purpose:** Detailed output to verify all technical indicators are calculated correctly for historical dates.

**Output Includes:**
- Price information
- Moving averages (D50, D100, D200)
- Support/resistance levels with quality ratings
- Volume profile (POC, VAH, VAL)
- RSI and Bollinger Bands
- Larsson trend states
- Signal classification

**Usage:**
```bash
python scripts/examples/test_qcom_details.py
```

---

## Notes

These scripts are **examples/debugging tools**, not formal unit tests. They:
- Demonstrate how to use the `as_of_date` parameter
- Help verify historical data functionality
- Show expected output format
- Useful for troubleshooting historical backtesting issues

For formal unit tests, see the `tests/` directory.
