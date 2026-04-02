from flask import Flask, jsonify, send_from_directory
import yfinance as yf
import time
import threading

app = Flask(__name__, static_folder='assets', template_folder='.')

# 🔥 Sectors
# 🔥 Lighter Sectors for Testing
sectors = {
    "IT": ["TCS.NS", "INFY.NS"],
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS"],
    "Auto": ["TATAMOTORS.NS", "MARUTI.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS"],
    "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS"],
    "Metal": ["TATASTEEL.NS", "JSWSTEEL.NS"],
    "Infra": ["LT.NS", "ULTRACEMCO.NS"],
    "Telecom": ["BHARTIARTL.NS"],
    "Finance": ["BAJFINANCE.NS"],
    "Power": ["NTPC.NS", "POWERGRID.NS"]
}

# 🔥 EMA simple formula
def simple_ema(prices, period):
    k = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = price * k + ema * (1 - k)
    return ema

# 🔥 Global storage for frontend
sector_results = []

def calculate_sector_data():
    global sector_results
    sector_results = []

    for sector, symbols in sectors.items():
        counts = {"20":0, "50":0, "100":0, "200":0}
        valid = 0

        for symbol in symbols:
            try:
                data = yf.Ticker(symbol).history(period="1y")['Close']
            except:
                continue

            if len(data) < 50:
                continue

            valid += 1
            last = data[-1]

            if last > simple_ema(data.values, 20): counts["20"] += 1
            if last > simple_ema(data.values, 50): counts["50"] += 1
            if last > simple_ema(data.values, 100): counts["100"] += 1
            if last > simple_ema(data.values, 200): counts["200"] += 1

            time.sleep(1)  # prevent overload

        sector_results.append({
            "sector": sector,
            "p20": (counts["20"]/valid)*100 if valid else 0,
            "p50": (counts["50"]/valid)*100 if valid else 0,
            "p100": (counts["100"]/valid)*100 if valid else 0,
            "p200": (counts["200"]/valid)*100 if valid else 0
        })

    # Sort by p20 after all sectors
    sector_results.sort(key=lambda x: x["p20"], reverse=True)

# 🔥 API Endpoint
@app.route("/api/ema")
def get_ema_data():
    return jsonify(sector_results)

# 🔥 Serve frontend
@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

# 🔥 Background updater
def background_updater(interval=60*15):  # 15 min
    while True:
        print("Starting sector EMA calculation...")
        calculate_sector_data()
        print("Finished sector EMA calculation ✅")
        time.sleep(interval)

if __name__ == "__main__":
    # Start background thread
    threading.Thread(target=background_updater, daemon=True).start()
    # Run app
    app.run(host="0.0.0.0", port=10000, debug=True)
