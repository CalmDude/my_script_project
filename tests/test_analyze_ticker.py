import pandas as pd
import numpy as np

from script import analyze_ticker


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
    res = analyze_ticker('FOO')
    assert res['ticker'] == 'FOO'
    assert 'signal' in res
    assert res['current_price'] == 123.45
    assert 'daily_poc' in res


def test_analyze_ticker_no_daily(monkeypatch):
    empty = pd.DataFrame()
    weekly = make_df(260).resample('W').last()
    info = {'regularMarketPrice': None}
    monkeypatch.setattr('yfinance.Ticker', lambda t: DummyTicker(info, empty, weekly))
    res = analyze_ticker('BAR')
    assert res['ticker'] == 'BAR'
    assert 'error' in res and 'no daily data' in res['error']
