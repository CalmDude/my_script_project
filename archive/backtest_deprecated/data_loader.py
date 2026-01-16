"""
Data Loader for GHB Strategy Backtest
Fetches historical price data for S&P 100/500 stocks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import List, Dict
import time


class DataLoader:
    """Handles downloading and caching historical stock data"""

    def __init__(self, config_path: str = "backtest/config.json"):
        """Initialize data loader with configuration"""
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.data_settings = self.config["data_settings"]
        self.backtest_settings = self.config["backtest_settings"]

        # Setup cache directory
        self.cache_path = Path(self.data_settings["cache_path"])
        self.cache_path.mkdir(parents=True, exist_ok=True)

        print(f"✅ DataLoader initialized")
        print(f"   Universe: {self.backtest_settings['universe'].upper()}")
        print(
            f"   Date Range: {self.backtest_settings['start_date']} to {self.backtest_settings['end_date']}"
        )

    def get_universe(self) -> List[str]:
        """Get list of tickers based on universe selection"""
        universe = self.backtest_settings["universe"].lower()

        if universe == "sp100":
            # S&P 100 - major large caps
            tickers = [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "NVDA",
                "META",
                "TSLA",
                "BRK.B",
                "UNH",
                "XOM",
                "JNJ",
                "JPM",
                "V",
                "PG",
                "MA",
                "HD",
                "CVX",
                "MRK",
                "ABBV",
                "PEP",
                "COST",
                "AVGO",
                "KO",
                "LLY",
                "ADBE",
                "MCD",
                "TMO",
                "CSCO",
                "ACN",
                "ABT",
                "WMT",
                "NFLX",
                "CRM",
                "DHR",
                "DIS",
                "VZ",
                "CMCSA",
                "NKE",
                "PFE",
                "INTC",
                "TXN",
                "AMD",
                "QCOM",
                "UNP",
                "PM",
                "BMY",
                "RTX",
                "NEE",
                "ORCL",
                "UPS",
                "HON",
                "INTU",
                "LOW",
                "BA",
                "T",
                "SPGI",
                "BLK",
                "CAT",
                "GE",
                "AMGN",
                "DE",
                "AXP",
                "MDT",
                "AMAT",
                "SCHW",
                "PLD",
                "GILD",
                "SBUX",
                "LMT",
                "SYK",
                "MMC",
                "TJX",
                "BKNG",
                "CI",
                "MDLZ",
                "VRTX",
                "ADI",
                "TMUS",
                "CVS",
                "ADP",
                "CB",
                "ZTS",
                "SO",
                "DUK",
                "NOC",
                "MO",
                "LRCX",
                "GD",
                "SLB",
                "USB",
                "PNC",
                "CME",
                "EOG",
                "ITW",
                "ICE",
                "BDX",
                "CL",
                "NSC",
                "REGN",
                "MU",
            ]
        elif universe == "sp100_optimized":
            # Qualified stocks from screening (meet volatility criteria)
            # Std Dev ≥30% OR Max Win ≥150% OR Avg Win ≥40%
            tickers = [
                "NVDA",
                "AVGO",
                "GE",
                "GOOGL",
                "LLY",
                "NFLX",
                "ORCL",
                "MU",
                "JPM",
                "META",
                "AMAT",
                "LRCX",
                "AMD",
                "CAT",
                "XOM",
                "MSFT",
                "AMZN",
                "COST",
                "VRTX",
                "NOC",
                "ICE",
                "EOG",
                "CVX",
                "T",
            ]
        elif universe == "nasdaq25":
            # 25-stock NASDAQ universe (legacy watchlist)
            # Backtested performance: 21.94% CAGR with 10% positions, 10 max holdings
            tickers = [
                "ALAB",
                "AMAT",
                "AMD",
                "ARM",
                "ASML",
                "AVGO",
                "BKNG",
                "CEG",
                "COST",
                "DASH",
                "FANG",
                "FTNT",
                "GOOG",
                "GOOGL",
                "META",
                "MRNA",
                "MRVL",
                "MSFT",
                "MU",
                "NFLX",
                "NVDA",
                "PANW",
                "PLTR",
                "TSLA",
                "TSM",
            ]
        elif universe == "nasdaq39":
            # Original GHB Strategy Universe (all 39 stocks from strategy guide)
            # Moderate volatile stocks meeting criteria:
            # Std Dev ≥30% OR Max Win ≥150% OR Avg Win ≥40%
            tickers = [
                "ALAB",
                "AMAT",
                "AMD",
                "AMZN",
                "ARM",
                "ASML",
                "AVGO",
                "BKNG",
                "CEG",
                "COST",
                "CPRT",
                "CRWD",
                "CTAS",
                "DASH",
                "FANG",
                "FTNT",
                "GOOG",
                "GOOGL",
                "ISRG",
                "KLAC",
                "LRCX",
                "MDB",
                "META",
                "MRNA",
                "MRVL",
                "MSFT",
                "MU",
                "NFLX",
                "NVDA",
                "ON",
                "PANW",
                "PCAR",
                "PLTR",
                "QCOM",
                "ROST",
                "TMUS",
                "TSLA",
                "TSM",
                "VRTX",
            ]
        elif universe == "sp500_optimized":
            # Top 25 qualified S&P 500 stocks from screening (meet volatility criteria)
            # Std Dev ≥30% OR Max Win ≥150% OR Avg Win ≥40%
            # Screened 490 stocks, 117 qualified (23.9%)
            tickers = [
                "NVDA",
                "SMCI",
                "AVGO",
                "GE",
                "TRGP",
                "STX",
                "AXON",
                "GOOGL",
                "VST",
                "LLY",
                "MPC",
                "PWR",
                "GOOG",
                "DECK",
                "MCK",
                "NFLX",
                "DVN",
                "CAH",
                "ANET",
                "ORCL",
                "MU",
                "WMB",
                "CEG",
                "APH",
                "JPM",
            ]
        elif universe == "sp500_unbiased_2020":
            # UNBIASED: Top 25 stocks selected using 2020 data only
            # Selected from S&P 500 members as of Jan 1, 2021
            # Criteria: Volatility >=25%, Volume >=2M, MarketCap >=$5B (all measured in 2020)
            # This avoids survivorship bias and optimization bias
            universe_file = Path("backtest/data/sp500_unbiased_2020.txt")
            if universe_file.exists():
                with open(universe_file, "r") as f:
                    tickers = [line.strip() for line in f if line.strip()]
            else:
                raise FileNotFoundError(
                    f"Universe file not found: {universe_file}\n"
                    "Run: python backtest/screen_unbiased_2020.py"
                )
        elif universe == "sp500_enhanced_2020":
            # ENHANCED: Top 25 stocks with Phase 1 improvements
            # Selected from S&P 500 members as of Jan 1, 2021 using 2020 data only
            # Improvements: Multi-factor scoring (Momentum 40% + Quality 30% + Vol 30%)
            #               Quality filters (exclude trash stocks)
            #               Sector limits (max 5 per sector for diversification)
            # Expected: +10-15% CAGR vs unbiased (25-30% vs 15.28%)
            universe_file = Path("backtest/data/sp500_enhanced_2020.txt")
            if universe_file.exists():
                with open(universe_file, "r") as f:
                    tickers = [line.strip() for line in f if line.strip()]
            else:
                raise FileNotFoundError(
                    f"Universe file not found: {universe_file}\n"
                    "Run: python backtest/screen_enhanced_2020.py"
                )
        elif universe == "sp500_enhanced_v2_2020":
            # ENHANCED V2: Phase 1B with corrected filters
            # Gentler filters: Debt<5.0, MarketCap>=$5B, RevGrowth>-20%
            # Momentum-focused: 50% Momentum + 35% Volatility + 15% Quality
            # Relaxed sector limits: Max 8 per sector (32%)
            universe_file = Path("backtest/data/sp500_enhanced_v2_2020.txt")
            if universe_file.exists():
                with open(universe_file, "r") as f:
                    tickers = [line.strip() for line in f if line.strip()]
            else:
                raise FileNotFoundError(
                    f"Universe file not found: {universe_file}\n"
                    "Run: python backtest/screen_enhanced_v2_2020.py"
                )
        elif universe == "custom_tech_stocks":
            # CUSTOM: User-selected tech stocks (ALAB, AYGO, MRVL, ARM, TSLA, NVDA, PLTR, NU, TSM, ASML, GOOG, AMD)
            universe_file = Path("backtest/data/custom_tech_stocks.txt")
            if universe_file.exists():
                with open(universe_file, "r") as f:
                    tickers = [line.strip() for line in f if line.strip()]
            else:
                raise FileNotFoundError(f"Universe file not found: {universe_file}")
        elif universe == "sp500":
            # S&P 500 - Full list of 500 large cap US stocks
            # This is a comprehensive list as of 2024
            tickers = [
                "A",
                "AAL",
                "AAPL",
                "ABBV",
                "ABNB",
                "ABT",
                "ACGL",
                "ACN",
                "ADBE",
                "ADI",
                "ADM",
                "ADP",
                "ADSK",
                "AEE",
                "AEP",
                "AES",
                "AFL",
                "AIG",
                "AIZ",
                "AJG",
                "AKAM",
                "ALB",
                "ALGN",
                "ALL",
                "ALLE",
                "AMAT",
                "AMCR",
                "AMD",
                "AME",
                "AMGN",
                "AMP",
                "AMT",
                "AMZN",
                "ANET",
                "ANSS",
                "AON",
                "AOS",
                "APA",
                "APD",
                "APH",
                "APTV",
                "ARE",
                "ATO",
                "AVB",
                "AVGO",
                "AVY",
                "AWK",
                "AXON",
                "AXP",
                "AZO",
                "BA",
                "BAC",
                "BALL",
                "BAX",
                "BBWI",
                "BBY",
                "BDX",
                "BEN",
                "BF-B",
                "BG",
                "BIIB",
                "BIO",
                "BK",
                "BKNG",
                "BKR",
                "BLDR",
                "BLK",
                "BMY",
                "BR",
                "BRK-B",
                "BRO",
                "BSX",
                "BWA",
                "BX",
                "BXP",
                "C",
                "CAG",
                "CAH",
                "CARR",
                "CAT",
                "CB",
                "CBOE",
                "CBRE",
                "CCI",
                "CCL",
                "CDNS",
                "CDW",
                "CE",
                "CEG",
                "CF",
                "CFG",
                "CHD",
                "CHRW",
                "CHTR",
                "CI",
                "CINF",
                "CL",
                "CLX",
                "CMA",
                "CMCSA",
                "CME",
                "CMG",
                "CMI",
                "CMS",
                "CNC",
                "CNP",
                "COF",
                "COO",
                "COP",
                "COR",
                "COST",
                "CPAY",
                "CPB",
                "CPRT",
                "CPT",
                "CRL",
                "CRM",
                "CSCO",
                "CSGP",
                "CSX",
                "CTAS",
                "CTLT",
                "CTRA",
                "CTSH",
                "CTVA",
                "CVS",
                "CVX",
                "CZR",
                "D",
                "DAL",
                "DAY",
                "DD",
                "DE",
                "DECK",
                "DFS",
                "DG",
                "DGX",
                "DHI",
                "DHR",
                "DIS",
                "DLR",
                "DLTR",
                "DOC",
                "DOV",
                "DOW",
                "DPZ",
                "DRI",
                "DTE",
                "DUK",
                "DVA",
                "DVN",
                "DXCM",
                "EA",
                "EBAY",
                "ECL",
                "ED",
                "EFX",
                "EG",
                "EIX",
                "EL",
                "ELV",
                "EMN",
                "EMR",
                "ENPH",
                "EOG",
                "EPAM",
                "EQIX",
                "EQR",
                "EQT",
                "ES",
                "ESS",
                "ETN",
                "ETR",
                "ETSY",
                "EVRG",
                "EW",
                "EXC",
                "EXPD",
                "EXPE",
                "EXR",
                "F",
                "FANG",
                "FAST",
                "FCX",
                "FDS",
                "FDX",
                "FE",
                "FFIV",
                "FI",
                "FICO",
                "FIS",
                "FITB",
                "FMC",
                "FOX",
                "FOXA",
                "FRT",
                "FSLR",
                "FTNT",
                "FTV",
                "GD",
                "GDDY",
                "GE",
                "GEHC",
                "GEN",
                "GEV",
                "GILD",
                "GIS",
                "GL",
                "GLW",
                "GM",
                "GNRC",
                "GOOG",
                "GOOGL",
                "GPC",
                "GPN",
                "GRMN",
                "GS",
                "GWW",
                "HAL",
                "HAS",
                "HBAN",
                "HCA",
                "HD",
                "HES",
                "HIG",
                "HII",
                "HLT",
                "HOLX",
                "HON",
                "HPE",
                "HPQ",
                "HRL",
                "HSIC",
                "HST",
                "HSY",
                "HUBB",
                "HUM",
                "HWM",
                "IBM",
                "ICE",
                "IDXX",
                "IEX",
                "IFF",
                "INCY",
                "INTC",
                "INTU",
                "INVH",
                "IP",
                "IPG",
                "IQV",
                "IR",
                "IRM",
                "ISRG",
                "IT",
                "ITW",
                "IVZ",
                "J",
                "JBHT",
                "JBL",
                "JCI",
                "JKHY",
                "JNJ",
                "JNPR",
                "JPM",
                "K",
                "KDP",
                "KEY",
                "KEYS",
                "KHC",
                "KIM",
                "KLAC",
                "KMB",
                "KMI",
                "KMX",
                "KO",
                "KR",
                "KVUE",
                "L",
                "LDOS",
                "LEN",
                "LH",
                "LHX",
                "LIN",
                "LKQ",
                "LLY",
                "LMT",
                "LNT",
                "LOW",
                "LRCX",
                "LULU",
                "LUV",
                "LVS",
                "LW",
                "LYB",
                "LYV",
                "MA",
                "MAA",
                "MAR",
                "MAS",
                "MCD",
                "MCHP",
                "MCK",
                "MCO",
                "MDLZ",
                "MDT",
                "MET",
                "META",
                "MGM",
                "MHK",
                "MKC",
                "MKTX",
                "MLM",
                "MMC",
                "MMM",
                "MNST",
                "MO",
                "MOH",
                "MOS",
                "MPC",
                "MPWR",
                "MRK",
                "MRNA",
                "MRO",
                "MS",
                "MSCI",
                "MSFT",
                "MSI",
                "MTB",
                "MTCH",
                "MTD",
                "MU",
                "NCLH",
                "NDAQ",
                "NDSN",
                "NEE",
                "NEM",
                "NFLX",
                "NI",
                "NKE",
                "NOC",
                "NOW",
                "NRG",
                "NSC",
                "NTAP",
                "NTRS",
                "NUE",
                "NVDA",
                "NVR",
                "NWS",
                "NWSA",
                "NXPI",
                "O",
                "ODFL",
                "OKE",
                "OMC",
                "ON",
                "ORCL",
                "ORLY",
                "OTIS",
                "OXY",
                "PANW",
                "PARA",
                "PAYC",
                "PAYX",
                "PCAR",
                "PCG",
                "PEG",
                "PEP",
                "PFE",
                "PFG",
                "PG",
                "PGR",
                "PH",
                "PHM",
                "PKG",
                "PLD",
                "PM",
                "PNC",
                "PNR",
                "PNW",
                "PODD",
                "POOL",
                "PPG",
                "PPL",
                "PRU",
                "PSA",
                "PSX",
                "PTC",
                "PWR",
                "PYPL",
                "QCOM",
                "QRVO",
                "RCL",
                "REG",
                "REGN",
                "RF",
                "RJF",
                "RL",
                "RMD",
                "ROK",
                "ROL",
                "ROP",
                "ROST",
                "RSG",
                "RTX",
                "RVTY",
                "SBAC",
                "SBUX",
                "SCHW",
                "SHW",
                "SJM",
                "SLB",
                "SMCI",
                "SNA",
                "SNPS",
                "SO",
                "SPG",
                "SPGI",
                "SRE",
                "STE",
                "STLD",
                "STT",
                "STX",
                "STZ",
                "SWK",
                "SWKS",
                "SYF",
                "SYK",
                "SYY",
                "T",
                "TAP",
                "TDG",
                "TDY",
                "TECH",
                "TEL",
                "TER",
                "TFC",
                "TFX",
                "TGT",
                "TJX",
                "TMO",
                "TMUS",
                "TPR",
                "TRGP",
                "TRMB",
                "TROW",
                "TRV",
                "TSCO",
                "TSLA",
                "TSN",
                "TT",
                "TTWO",
                "TXN",
                "TXT",
                "TYL",
                "UAL",
                "UBER",
                "UDR",
                "UHS",
                "ULTA",
                "UNH",
                "UNP",
                "UPS",
                "URI",
                "USB",
                "V",
                "VICI",
                "VLO",
                "VLTO",
                "VMC",
                "VRSK",
                "VRSN",
                "VRTX",
                "VST",
                "VTR",
                "VTRS",
                "VZ",
                "WAB",
                "WAT",
                "WBA",
                "WBD",
                "WDC",
                "WEC",
                "WELL",
                "WFC",
                "WM",
                "WMB",
                "WMT",
                "WRB",
                "WRK",
                "WST",
                "WTW",
                "WY",
                "WYNN",
                "XEL",
                "XOM",
                "XYL",
                "YUM",
                "ZBH",
                "ZBRA",
                "ZTS",
            ]
        else:
            raise ValueError(f"Unknown universe: {universe}")

        print(f"📊 Universe contains {len(tickers)} stocks")
        return tickers

    def download_historical_data(
        self, tickers: List[str], force_refresh: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Download historical data for list of tickers
        Returns dict of {ticker: dataframe}
        """
        start_date = self.backtest_settings["start_date"]
        end_date = self.backtest_settings["end_date"]

        # Add buffer for technical indicators (need 200 days before start)
        start_date_buffered = (
            pd.to_datetime(start_date) - timedelta(days=365)
        ).strftime("%Y-%m-%d")

        cache_file = (
            self.cache_path / f"historical_data_{start_date}_{end_date}.parquet"
        )

        # Check cache
        if (
            not force_refresh
            and self.data_settings["cache_enabled"]
            and cache_file.exists()
        ):
            print(f"📦 Loading cached data from {cache_file}")
            df_all = pd.read_parquet(cache_file)

            # Split by ticker and filter to requested tickers only
            data_dict = {}
            for ticker in tickers:
                if ticker in df_all["Ticker"].values:
                    data_dict[ticker] = df_all[df_all["Ticker"] == ticker].drop(
                        "Ticker", axis=1
                    )

            print(f"✅ Loaded {len(data_dict)} stocks from cache")
            return data_dict

        # Download fresh data
        print(f"📥 Downloading historical data for {len(tickers)} stocks...")
        print(f"   Date range: {start_date_buffered} to {end_date}")
        print("   This will take 5-10 minutes for first run...\n")

        data_dict = {}
        failed_tickers = []

        for i, ticker in enumerate(tickers, 1):
            try:
                print(f"  [{i:3d}/{len(tickers)}] Downloading {ticker:6s}...", end="\r")

                stock = yf.Ticker(ticker)
                df = stock.history(
                    start=start_date_buffered, end=end_date, interval="1d"
                )

                if df.empty or len(df) < 200:
                    failed_tickers.append(ticker)
                    continue

                # Clean data
                df = df[["Open", "High", "Low", "Close", "Volume"]]
                df.index.name = "Date"
                df = df.reset_index()

                # Remove timezone to avoid comparison issues
                if df["Date"].dt.tz is not None:
                    df["Date"] = df["Date"].dt.tz_localize(None)

                data_dict[ticker] = df

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                print(f"\n❌ Error downloading {ticker}: {str(e)}")
                failed_tickers.append(ticker)
                continue

        print(f"\n✅ Download complete!")
        print(f"   Successful: {len(data_dict)} stocks")
        print(f"   Failed: {len(failed_tickers)} stocks")

        if failed_tickers:
            print(f"   Failed tickers: {', '.join(failed_tickers[:10])}...")

        # Cache the data
        if self.data_settings["cache_enabled"] and len(data_dict) > 0:
            print(f"\n💾 Caching data to {cache_file}...")

            # Combine all dataframes
            df_list = []
            for ticker, df in data_dict.items():
                df_copy = df.copy()
                df_copy["Ticker"] = ticker
                df_list.append(df_copy)

            df_all = pd.concat(df_list, ignore_index=True)
            df_all.to_parquet(cache_file, compression="gzip")

            print(f"✅ Data cached successfully")

        return data_dict

    def get_sp100_tickers(self) -> List[str]:
        """Convenience method to get S&P 100 list"""
        return self.get_universe()


if __name__ == "__main__":
    # Test the data loader
    print("=" * 80)
    print("Testing DataLoader")
    print("=" * 80)

    loader = DataLoader()
    tickers = loader.get_universe()

    print(f"\n📊 Will download data for {len(tickers)} stocks")
    print(f"   First 10: {', '.join(tickers[:10])}")

    # Download data
    data = loader.download_historical_data(tickers)

    # Show sample
    if data:
        sample_ticker = list(data.keys())[0]
        print(f"\n📈 Sample data for {sample_ticker}:")
        print(data[sample_ticker].tail())
        print(f"\n   Shape: {data[sample_ticker].shape}")
        print(
            f"   Date range: {data[sample_ticker]['Date'].min()} to {data[sample_ticker]['Date'].max()}"
        )
