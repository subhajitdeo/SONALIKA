from flask import Flask, jsonify
import yfinance as yf
import time
import threading

app = Flask(__name__)

# 🔥 Sectors
sectors = {
    "IT": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS","LTIM.NS"],
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","AXISBANK.NS","KOTAKBANK.NS","INDUSINDBK.NS"],
    "Auto": ["TATAMOTORS.NS","MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","EICHERMOT.NS"],
    "FMCG": ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS","BRITANNIA.NS","DABUR.NS","MARICO.NS"],
    "Pharma": ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","LUPIN.NS","AUROPHARMA.NS"],
    "Energy": ["RELIANCE.NS","ONGC.NS","BPCL.NS","IOC.NS","GAIL.NS","ADANIGREEN.NS"],
    "Metal": ["TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","COALINDIA.NS","NMDC.NS"],
    "Infra": ["LT.NS","ULTRACEMCO.NS","GRASIM.NS","SIEMENS.NS"],
    "Telecom": ["BHARTIARTL.NS","INDUSTOWER.NS"],
    "Finance": ["BAJFINANCE.NS","BAJAJFINSV.NS","SBILIFE.NS","HDFCLIFE.NS","ICICIPRULI.NS"],
    "Power": ["NTPC.NS","POWERGRID.NS","ADANIPOWER.NS","TATAPOWER.NS"]
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

        # Sort by p20 after each sector
        sector_results.sort(key=lambda x: x["p20"], reverse=True)

@app.route("/api/ema")
def get_ema_data():
    return jsonify(sector_results)

# 🔥 Background thread to update sector data every N minutes
def background_updater(interval=60*15):  # 15 min
    while True:
        print("Starting sector EMA calculation...")
        calculate_sector_data()
        print("Finished sector EMA calculation ✅")
        time.sleep(interval)

if __name__ == "__main__":
    # Start background updater thread
    threading.Thread(target=background_updater, daemon=True).start()
    app.run(debug=True)
