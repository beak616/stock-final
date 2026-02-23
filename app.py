from flask import Flask, render_template, request
import yfinance as yf
import os
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        symbols_input = request.form.get("symbols")

        # 支援空格或逗號分隔
        symbols = symbols_input.replace(",", " ").split()

        for symbol in symbols:
            try:
                data = yf.download(symbol, period="60d")

                if len(data) < 20:
                    results.append({
                        "symbol": symbol,
                        "error": "資料不足"
                    })
                    continue

                data["MA5"] = data["Close"].rolling(5).mean()
                data["MA20"] = data["Close"].rolling(20).mean()

                today_ma5 = data["MA5"].iloc[-1]
                today_ma20 = data["MA20"].iloc[-1]

                yesterday_ma5 = data["MA5"].iloc[-2]
                yesterday_ma20 = data["MA20"].iloc[-2]
                
                if ((yesterday_ma20 - yesterday_ma5 > 0 and today_ma5 - today_ma20 > 0) or
                    (yesterday_ma20 - yesterday_ma5 < 0 and today_ma20 - today_ma5 > 0)):
                    signal = "go trans"
                else:
                    signal = "do nothing"
                alert = "-"
                for i in range(1, 7):  # 過去七天
                    today_diff = data["MA5"].iloc[-i] - data["MA20"].iloc[-i]
                    yesterday_diff = data["MA5"].iloc[-i-1] - data["MA20"].iloc[-i-1]
                    if (today_diff > 0 and yesterday_diff < 0) or (today_diff < 0 and yesterday_diff > 0):
                        alert = "intersect"
                        break
                results.append({
                    "symbol": symbol,
                    "today_ma5": round(today_ma5, 2),
                    "today_ma20": round(today_ma20, 2),
                    "yesterday_ma5": round(yesterday_ma5, 2),
                    "yesterday_ma20": round(yesterday_ma20, 2),
                    "signal": signal,
                    "alert": alert
                })
                

            except Exception as e:
                results.append({
                    "symbol": symbol,
                    "error": str(e)
                })

    return render_template("ind.html", results=results)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
