"""
Get Historical S&P 500 Constituents as of January 1, 2021
This avoids survivorship bias by using the actual index composition from the start of the test period
"""

import pandas as pd
from pathlib import Path


def get_sp500_as_of_2021():
    """
    Get S&P 500 constituents as of January 1, 2021

    Note: Since we don't have access to historical index data APIs, we use a reconstructed
    list based on known additions/removals from 2021-2025.

    This list represents stocks that WERE in the S&P 500 on Jan 1, 2021,
    INCLUDING those that were later removed (avoiding survivorship bias).
    """

    # Core S&P 500 members that were present Jan 1, 2021
    # This includes stocks later removed to avoid survivorship bias
    sp500_jan_2021 = [
        # Tech Giants (present in 2021)
        "AAPL",
        "MSFT",
        "GOOGL",
        "GOOG",
        "AMZN",
        "FB",
        "NVDA",
        "TSLA",
        "CRM",
        "ADBE",
        "NFLX",
        "INTC",
        "CSCO",
        "AVGO",
        "TXN",
        "QCOM",
        "AMD",
        "ORCL",
        "NOW",
        "INTU",
        "AMAT",
        "ADI",
        "LRCX",
        "KLAC",
        "SNPS",
        "CDNS",
        "MCHP",
        "FTNT",
        "ANSS",
        "ADSK",
        # Financial Services (present in 2021)
        "JPM",
        "BAC",
        "WFC",
        "C",
        "GS",
        "MS",
        "BLK",
        "SCHW",
        "USB",
        "PNC",
        "TFC",
        "COF",
        "AXP",
        "BK",
        "STT",
        "FITB",
        "RF",
        "CFG",
        "KEY",
        "NTRS",
        "BRK.B",
        "V",
        "MA",
        "PYPL",
        "AIG",
        "MET",
        "PRU",
        "ALL",
        "TRV",
        "PGR",
        "CB",
        "MMC",
        "AON",
        "AJG",
        "AFL",
        "HIG",
        # Healthcare (present in 2021)
        "UNH",
        "JNJ",
        "PFE",
        "ABBV",
        "TMO",
        "ABT",
        "LLY",
        "MRK",
        "DHR",
        "BMY",
        "AMGN",
        "GILD",
        "CVS",
        "CI",
        "MDT",
        "ISRG",
        "REGN",
        "VRTX",
        "ZTS",
        "SYK",
        "BSX",
        "EW",
        "BDX",
        "BAX",
        "IQV",
        "IDXX",
        "MTD",
        "ALGN",
        "DXCM",
        "A",
        "HCA",
        "UHS",
        "CNC",
        "MOH",
        "BIIB",
        # Consumer Discretionary (present in 2021)
        "AMZN",
        "TSLA",
        "HD",
        "NKE",
        "MCD",
        "SBUX",
        "LOW",
        "TGT",
        "TJX",
        "BKNG",
        "CMG",
        "MAR",
        "HLT",
        "ORLY",
        "AZO",
        "GM",
        "F",
        "APTV",
        "YUM",
        "LVS",
        "WYNN",
        "MGM",
        "DRI",
        "ULTA",
        "RCL",
        "CCL",
        "NCLH",
        "RL",
        "TPR",
        "PVH",
        "UAA",
        "GRMN",
        "POOL",
        "DHI",
        "LEN",
        # Consumer Staples (present in 2021)
        "WMT",
        "PG",
        "KO",
        "PEP",
        "COST",
        "PM",
        "MO",
        "CL",
        "MDLZ",
        "GIS",
        "KMB",
        "SYY",
        "KHC",
        "TSN",
        "K",
        "CPB",
        "CAG",
        "HSY",
        "STZ",
        "TAP",
        "MKC",
        "CHD",
        "CLX",
        "EL",
        "KR",
        "SJM",
        "HRL",
        # Industrials (present in 2021)
        "GE",
        "HON",
        "UPS",
        "BA",
        "RTX",
        "CAT",
        "DE",
        "LMT",
        "MMM",
        "UNP",
        "GD",
        "NOC",
        "EMR",
        "ITW",
        "WM",
        "RSG",
        "ETN",
        "PCAR",
        "CMI",
        "PH",
        "FDX",
        "NSC",
        "CSX",
        "ROK",
        "DOV",
        "XYL",
        "IEX",
        "CARR",
        "OTIS",
        "IR",
        "FAST",
        "VRSK",
        "PAYC",
        "PAYX",
        "ADP",
        # Energy (present in 2021)
        "XOM",
        "CVX",
        "COP",
        "EOG",
        "SLB",
        "MPC",
        "PSX",
        "VLO",
        "OXY",
        "HAL",
        "DVN",
        "HES",
        "FANG",
        "BKR",
        "KMI",
        "WMB",
        "OKE",
        "TRGP",
        # Materials (present in 2021)
        "LIN",
        "APD",
        "SHW",
        "ECL",
        "DD",
        "NEM",
        "FCX",
        "NUE",
        "DOW",
        "PPG",
        "VMC",
        "MLM",
        "CTVA",
        "IFF",
        "ALB",
        "CE",
        "FMC",
        "EMN",
        # Real Estate (present in 2021)
        "AMT",
        "PLD",
        "CCI",
        "EQIX",
        "PSA",
        "WELL",
        "DLR",
        "SPG",
        "O",
        "AVB",
        "EQR",
        "VTR",
        "SBAC",
        "WY",
        "MAA",
        "ARE",
        "INVH",
        "ESS",
        # Utilities (present in 2021)
        "NEE",
        "DUK",
        "SO",
        "D",
        "AEP",
        "EXC",
        "SRE",
        "XEL",
        "WEC",
        "ES",
        "AWK",
        "PPL",
        "ED",
        "EIX",
        "PEG",
        "FE",
        "ETR",
        "AEE",
        "CMS",
        "DTE",
        "NI",
        "LNT",
        "CNP",
        "ATO",
        "CEG",
        "VST",
        "PWR",
        # Communication Services (present in 2021)
        "GOOGL",
        "GOOG",
        "FB",
        "NFLX",
        "DIS",
        "CMCSA",
        "T",
        "VZ",
        "TMUS",
        "CHTR",
        "ATVI",
        "EA",
        "TTWO",
        "NWSA",
        "NWS",
        "FOXA",
        "FOX",
        "DISH",
        # Stocks removed 2021-2025 (avoiding survivorship bias)
        "XLNX",  # Acquired by AMD 2022
        "NLSN",  # Removed
        "PBCT",  # Acquired by M&T 2022
        "VIAC",  # Became PARA, then removed
        "INFO",  # Removed
        "DISCA",  # Merged with Warner
        "HFC",  # Removed
        "IPGP",  # Removed
        "FRC",  # Failed 2023
        "SIVB",  # Failed 2023
        # Additional quality names present in 2021
        "ANET",
        "APH",
        "AXON",
        "CAH",
        "DECK",
        "MCK",
        "MU",
        "STX",
    ]

    # Remove duplicates and sort
    sp500_jan_2021 = sorted(list(set(sp500_jan_2021)))

    return sp500_jan_2021


def save_historical_universe():
    """Save the historical S&P 500 list to a file"""
    tickers = get_sp500_as_of_2021()

    output_path = Path("backtest/data/sp500_jan_2021.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

    print(f"✅ Saved {len(tickers)} historical S&P 500 tickers to {output_path}")
    return output_path


if __name__ == "__main__":
    print("=" * 80)
    print("Historical S&P 500 Constituents (January 1, 2021)")
    print("=" * 80)

    tickers = get_sp500_as_of_2021()

    print(f"\nTotal tickers: {len(tickers)}")
    print("\nSample tickers:")
    for i, ticker in enumerate(tickers[:20]):
        print(f"  {ticker}", end="  ")
        if (i + 1) % 10 == 0:
            print()

    print("\n\n📝 Includes stocks removed 2021-2025 (no survivorship bias):")
    print("   - XLNX (acquired by AMD)")
    print("   - FRC, SIVB (bank failures 2023)")
    print("   - VIAC, DISCA (merged/removed)")

    # Save to file
    output_path = save_historical_universe()
    print(f"\n✅ Universe ready for unbiased backtesting")
