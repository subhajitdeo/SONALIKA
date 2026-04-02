from flask import Flask, jsonify
from nsetools import Nse
import math

app = Flask(__name__)
nse = Nse()

# Stocks by sector
sectors = {
    "IT": ["TCS","INFY","WIPRO","HCLTECH","TECHM","LTIM"],
    "Banking": ["HDFCBANK","ICICIBANK","SBIN","AXISBANK","KOTAKBANK","INDUSINDBK"],
    "Auto": ["TATAMOTORS","MARUTI","M&M","BAJAJ-AUTO","HEROMOTOCO","EICHERMOT"],
    "FMCG": ["HINDUNILVR","ITC","NESTLEIND","BRITANNIA","DABUR","MARICO"],
    "Pharma": ["SUNPHARMA","DRREDDY","CIPLA","DIVISLAB","LUPIN","AUROPHARMA"],
    "Energy": ["RELIANCE","ONGC","BPCL","IOC","GAIL","ADANIGREEN"],
    "Metal": ["TATASTEEL","JSWSTEEL","HINDALCO","COALINDIA","NMDC"],
    "Infra": ["LT","ULTRACEMCO","GRASIM","SIEMENS"],
    "Telecom": ["BHARTIARTL","INDUSTOWER"],
    "Finance": ["BAJFINANCE","BAJAJFINSV","SBILIFE","HDFCLIFE","ICICIPRULI"],
    "Power": ["NTPC","POWERGRID","ADANIPOWER","TATAPOWER"]
}

# Function to calculate EMA
def calculate_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

# Helper to get last N closing prices from NSE
def get_close_prices(symbol, n=200):
    try:
        data = nse.get_history(symbol=symbol)
        if not data:
            return []
        # Sort by date ascending and get last n closing prices
        closes = [day['Close'] for day in sorted(data, key=lambda x: x['date'])]
        return closes[-n:]
    except:
        return []

@app.route("/update-ema")
def update_ema():
    results = []

    for sector, stocks in sectors.items():
        valid = 0
        c20 = c50 = c100 = c200 = 0

        for symbol in stocks:
            closes = get_close_prices(symbol)
            if len(closes) < 20:  # skip if not enough data
                continue
            valid += 1
            last_close = closes[-1]

            if last_close > calculate_ema(closes,20): c20 += 1
            if last_close > calculate_ema(closes,50): c50 += 1
            if last_close > calculate_ema(closes,100): c100 += 1
            if last_close > calculate_ema(closes,200): c200 += 1

        results.append({
            "sector": sector,
            "p20": (c20/valid*100) if valid else 0,
            "p50": (c50/valid*100) if valid else 0,
            "p100": (c100/valid*100) if valid else 0,
            "p200": (c200/valid*100) if valid else 0
        })

    # Sort by EMA20 descending
    results.sort(key=lambda x: x['p20'], reverse=True)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
