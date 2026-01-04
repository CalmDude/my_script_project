import numpy as np
from script import analyze_ticker, analyze_basket
import traceback

# Test the Lower Risk AI Basket
tickers = ['AMD', 'AVGO', 'ALAB', 'MRVL']

print("Testing individual tickers:")
for t in tickers:
    r = analyze_ticker(t, 60, 52)
    print(f"{t}: w200 = {r.get('w200')}")

print("\n" + "="*50)
print("Testing basket analysis:")
try:
    result = analyze_basket('Lower Risk AI Basket', tickers, 60, 52)
    if 'error' in result:
        print(f"ERROR: {result['error']}")
    else:
        print("SUCCESS!")
        print(f"Ticker: {result['ticker']}")
        print(f"Signal: {result['signal']}")
        print(f"Price: {result['current_price']}")
        print(f"w200: {result['w200']}")
        print(f"Notes: {result['notes']}")
except Exception as e:
    print(f"EXCEPTION: {e}")
    traceback.print_exc()
