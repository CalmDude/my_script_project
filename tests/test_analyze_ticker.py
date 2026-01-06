import pandas as pd
import numpy as np
from unittest.mock import patch

from technical_analysis import analyze_ticker


class DummyTicker:
    def __init__(self, info, daily_df, weekly_df):
        self._info = info
        self._daily = daily_df
        self._weekly = weekly_df

    @property
    def info(self):
        return self._info

    def history(self, period="3y", interval=None):
        if interval == "1wk":
            return self._weekly
        return self._daily


def make_df(n, start='2020-01-01'):
    dates = pd.date_range(start=start, periods=n, freq='D')
    df = pd.DataFrame({
        'High': np.linspace(100, 200, n),
        'Low': np.linspace(90, 190, n),
        'Close': np.linspace(95, 195, n),
        'Volume': np.arange(n) + 1000
    }, index=dates)
    return df


def test_analyze_ticker_success(monkeypatch):
    daily = make_df(220)
    weekly = make_df(260).resample('W').last()
    info = {'regularMarketPrice': 123.45}
    monkeypatch.setattr('yfinance.Ticker', lambda t: DummyTicker(info, daily, weekly))

    # Mock the delay and cache functions to speed up tests
    with patch('technical_analysis._smart_delay'), \
         patch('technical_analysis._load_from_cache', return_value=None), \
         patch('technical_analysis._save_to_cache'):
        res = analyze_ticker('FOO')

    assert res['ticker'] == 'FOO'
    assert 'signal' in res
    assert res['current_price'] == 123.45
    assert 's1' in res  # Check for support level instead of daily_poc
    assert 'r1' in res  # Check for resistance level


def test_analyze_ticker_no_daily(monkeypatch):
    empty = pd.DataFrame()
    weekly = make_df(260).resample('W').last()
    info = {'regularMarketPrice': None}
    monkeypatch.setattr('yfinance.Ticker', lambda t: DummyTicker(info, empty, weekly))

    # Mock the delay and cache functions
    with patch('technical_analysis._smart_delay'), \
         patch('technical_analysis._load_from_cache', return_value=None), \
         patch('technical_analysis._save_to_cache'):
        res = analyze_ticker('BAR')

    assert res['ticker'] == 'BAR'
    assert 'error' in res and 'no daily data' in res['error']
