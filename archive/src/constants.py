"""
Configuration Constants for Portfolio Analysis

Centralizes magic numbers and configuration values used throughout the codebase.
"""

# ============================================================================
# CACHING CONFIGURATION
# ============================================================================
CACHE_TTL_HOURS = 24  # Cache time-to-live in hours
CACHE_DIR_NAME = ".scanner_cache"  # Cache directory name

# ============================================================================
# API RATE LIMITING
# ============================================================================
SMART_DELAY_MIN_SECONDS = 1.0  # Minimum delay between API calls
SMART_DELAY_MAX_SECONDS = 2.0  # Maximum delay between API calls
DEFAULT_CONCURRENCY = 4  # Default number of concurrent API workers

# ============================================================================
# TECHNICAL ANALYSIS PARAMETERS
# ============================================================================

# Support/Resistance Detection
SWING_POINT_STRENGTH = 10  # Lookback period for swing point detection
RESISTANCE_STRENGTH = 5  # Lower strength for resistance detection (more sensitive)
MAX_SR_LEVELS = 3  # Maximum number of support/resistance levels to identify
MAX_RESISTANCE_DISTANCE_PCT = 0.30  # Filter resistances >30% above current price

# Volume Profile Parameters
VPVR_60DAY_PERIOD = 60  # 60-day volume profile for short-term analysis
VPVR_52WEEK_PERIOD = 252  # 52-week volume profile for long-term context
VPVR_NUM_BINS = 50  # Number of price bins for volume profile calculation

# Moving Average Parameters
MA_PERIODS_DAILY = [20, 50, 100, 200]  # Daily moving average periods
MA_PERIODS_WEEKLY = [10, 20, 200]  # Weekly moving average periods

# ============================================================================
# BUY/SELL QUALITY ASSESSMENT
# ============================================================================

# Tolerance thresholds for level alignment
SUPPORT_ALIGNMENT_TOLERANCE_PCT = 0.03  # 3% tolerance for POC/HVN support alignment
RESISTANCE_ALIGNMENT_TOLERANCE_PCT = (
    0.03  # 3% tolerance for POC/HVN resistance alignment
)
VALUE_AREA_PROXIMITY_PCT = 0.03  # 3% proximity to Value Area boundaries

# Price extension thresholds
EXTENDED_THRESHOLD_PCT = 0.10  # >10% above D100/VAH = EXTENDED
EXTENDED_DISTANCE_FROM_MA_PCT = 0.10  # 10% above all MAs threshold

# ============================================================================
# POSITION MANAGEMENT
# ============================================================================

# Buy tranche allocation percentages (sum = 1.0)
BUY_TRANCHE_S3_PCT = 0.40  # 40% at deepest support (S3)
BUY_TRANCHE_S2_PCT = 0.35  # 35% at mid support (S2)
BUY_TRANCHE_S1_PCT = 0.25  # 25% at nearest support (S1)

# Reduction targets by signal type (as decimal: 0.20 = 20%)
REDUCTION_HOLD_REDUCE_PCT = 0.20  # Keep 80% - weekly bull intact
REDUCTION_REDUCE_PCT = 0.40  # Keep 60% - weekly bearish, daily bounce
REDUCTION_LIGHT_CASH_PCT = 0.60  # Keep 40% - both neutral/unclear
REDUCTION_CASH_PCT = 0.80  # Keep 20% - serious warning
REDUCTION_FULL_CASH_PCT = 1.00  # Full exit - both bearish (phased)

# ============================================================================
# REPORT GENERATION
# ============================================================================

# PDF Report Parameters
PDF_PAGE_SIZE = "letter"
PDF_MARGIN_INCHES = 30  # ReportLab units (1/72 inch)

# Excel Report Parameters
EXCEL_MAX_COLUMN_WIDTH = 50  # Maximum column width in Excel
EXCEL_COLUMN_WIDTH_PADDING = 2  # Padding added to calculated column width

# Archive Management
MAX_ARCHIVE_FILES_BEFORE_CLEANUP = 20  # Max files before triggering archive
ARCHIVE_RETENTION_DAYS = 90  # Keep archive files for 90 days

# ============================================================================
# DATA TIMEFRAMES
# ============================================================================

# Historical data periods (for yfinance API)
DAILY_BARS_DEFAULT = 60  # Default daily bars to analyze
WEEKLY_BARS_DEFAULT = 52  # Default weekly bars to analyze
HISTORY_PERIOD_DAILY = "3y"  # 3 years of daily data
HISTORY_PERIOD_WEEKLY = "3y"  # 3 years of weekly data (resampled)

# ============================================================================
# LARSSON DECISION TABLE SIGNALS
# ============================================================================

# Signal names (for reference and validation)
SIGNAL_FULL_HOLD_ADD = "FULL HOLD + ADD"
SIGNAL_HOLD = "HOLD"
SIGNAL_HOLD_REDUCE = "HOLD MOST + REDUCE"
SIGNAL_SCALE_IN = "SCALE IN"
SIGNAL_LIGHT_CASH = "LIGHT / CASH"
SIGNAL_CASH = "CASH"
SIGNAL_REDUCE = "REDUCE"
SIGNAL_FULL_CASH = "FULL CASH / DEFEND"
SIGNAL_INSUFFICIENT_DATA = "INSUFFICIENT DATA"

ALL_SIGNALS = [
    SIGNAL_FULL_HOLD_ADD,
    SIGNAL_HOLD,
    SIGNAL_HOLD_REDUCE,
    SIGNAL_SCALE_IN,
    SIGNAL_LIGHT_CASH,
    SIGNAL_CASH,
    SIGNAL_REDUCE,
    SIGNAL_FULL_CASH,
    SIGNAL_INSUFFICIENT_DATA,
]

# Signals that trigger buy actions
BUY_SIGNALS = [SIGNAL_FULL_HOLD_ADD]

# Signals that trigger sell/reduce actions
SELL_SIGNALS = [
    SIGNAL_HOLD_REDUCE,
    SIGNAL_REDUCE,
    SIGNAL_LIGHT_CASH,
    SIGNAL_CASH,
    SIGNAL_FULL_CASH,
]

# ============================================================================
# QUALITY RATINGS
# ============================================================================

# Buy quality ratings (in order of preference)
QUALITY_EXCELLENT = "EXCELLENT"
QUALITY_GOOD = "GOOD"
QUALITY_OK = "OK"
QUALITY_CAUTION = "CAUTION"
QUALITY_EXTENDED = "EXTENDED"

# Sell quality ratings
QUALITY_STRONG = "STRONG"
QUALITY_MODERATE = "MODERATE"
QUALITY_WEAK = "WEAK"

# ============================================================================
# VALIDATION PATTERNS
# ============================================================================

# Ticker symbol validation regex
TICKER_PATTERN = r"^[A-Z0-9\.\-]+$"

# Basket name format in stocks.txt
BASKET_PATTERN = r"\[([^\]]+)\]\s*(.+)"
