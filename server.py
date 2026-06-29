from flask import Flask, request, send_from_directory, Response, jsonify
import requests

app = Flask(__name__, static_folder=".")

ALLOWED_DOMAINS = [
    "https://query1.finance.yahoo.com",
    "https://query2.finance.yahoo.com"
]


@app.route("/")
def index():
    return send_from_directory(".", "wealthgrow_agent.html")


@app.route("/wealthgrow_agent.html")
def html():
    return send_from_directory(".", "wealthgrow_agent.html")


@app.route("/api/proxy")
def proxy():
    url = request.args.get("url")

    if not url:
        return Response("Missing url", status=400)

    if not any(url.startswith(domain) for domain in ALLOWED_DOMAINS):
        return Response("Blocked domain", status=403)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type", "application/json")
        )

    except Exception as e:
        return Response(str(e), status=500)


@app.route("/api/market")
def market():
    result = {
        "kospi": None,
        "usdkrw": None
    }

    kospi_candidates = ["^KS11", "KS11.KS"]
    fx_candidates = ["KRW=X", "USDKRW=X"]

    for symbol in kospi_candidates:
        data = get_yahoo_chart_simple(symbol)
        if data:
            result["kospi"] = data
            break

    for symbol in fx_candidates:
        data = get_yahoo_chart_simple(symbol)
        if data:
            result["usdkrw"] = data
            break

    return jsonify(result)


def get_yahoo_chart_simple(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        json_data = response.json()
        chart = json_data.get("chart", {}).get("result", [])

        if not chart:
            return None

        quote = chart[0].get("indicators", {}).get("quote", [])

        if not quote:
            return None

        closes = quote[0].get("close", [])
        closes = [v for v in closes if v is not None]

        if len(closes) < 2:
            return None

        current = closes[-1]
        previous = closes[-2]
        change = current - previous
        change_rate = change / previous * 100

        return {
            "symbol": symbol,
            "current": current,
            "previous": previous,
            "change": change,
            "changeRate": change_rate
        }

    except Exception:
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)