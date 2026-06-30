from flask import Flask, request, send_from_directory, Response, jsonify
import requests
import os
import math
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__, static_folder=".")

HTML_FILE = "wealthgrow_agent.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

ALLOWED_DOMAINS = [
    "https://query1.finance.yahoo.com",
    "https://query2.finance.yahoo.com"
]

TOP5_CACHE = {
    "date": None,
    "data": None
}

SEARCH_MASTER = [
    {"name": "SK하이닉스", "code": "000660", "symbol": "000660.KS", "market": "KOSPI", "keywords": ["하이닉스", "하이", "sk", "hynix", "skhynix"]},
    {"name": "삼성전자", "code": "005930", "symbol": "005930.KS", "market": "KOSPI", "keywords": ["삼성", "삼전", "samsung"]},
    {"name": "삼성SDI", "code": "006400", "symbol": "006400.KS", "market": "KOSPI", "keywords": ["삼성sdi", "sdi"]},
    {"name": "LG에너지솔루션", "code": "373220", "symbol": "373220.KS", "market": "KOSPI", "keywords": ["lg엔솔", "엔솔", "lg energy"]},
    {"name": "LG화학", "code": "051910", "symbol": "051910.KS", "market": "KOSPI", "keywords": ["lg화학", "엘지화학"]},
    {"name": "현대차", "code": "005380", "symbol": "005380.KS", "market": "KOSPI", "keywords": ["현대", "현대자동차", "hyundai"]},
    {"name": "기아", "code": "000270", "symbol": "000270.KS", "market": "KOSPI", "keywords": ["kia"]},
    {"name": "NAVER", "code": "035420", "symbol": "035420.KS", "market": "KOSPI", "keywords": ["네이버", "naver"]},
    {"name": "카카오", "code": "035720", "symbol": "035720.KS", "market": "KOSPI", "keywords": ["kakao"]},
    {"name": "한화에어로스페이스", "code": "012450", "symbol": "012450.KS", "market": "KOSPI", "keywords": ["한화", "한화에어로", "hanwha", "aerospace"]},
    {"name": "한미반도체", "code": "042700", "symbol": "042700.KS", "market": "KOSPI", "keywords": ["한미", "hanmi"]},
    {"name": "두산에너빌리티", "code": "034020", "symbol": "034020.KS", "market": "KOSPI", "keywords": ["두산", "두산에너", "doosan"]},
    {"name": "포스코퓨처엠", "code": "003670", "symbol": "003670.KS", "market": "KOSPI", "keywords": ["포스코퓨처엠", "퓨처엠", "posco"]},
    {"name": "셀트리온", "code": "068270", "symbol": "068270.KS", "market": "KOSPI", "keywords": ["셀트", "celltrion"]},
    {"name": "삼성바이오로직스", "code": "207940", "symbol": "207940.KS", "market": "KOSPI", "keywords": ["삼바", "삼성바이오", "bio"]},
    {"name": "에코프로비엠", "code": "247540", "symbol": "247540.KQ", "market": "KOSDAQ", "keywords": ["에코프로", "비엠", "ecopro"]},
    {"name": "에코프로", "code": "086520", "symbol": "086520.KQ", "market": "KOSDAQ", "keywords": ["ecopro"]},
    {"name": "HLB", "code": "028300", "symbol": "028300.KQ", "market": "KOSDAQ", "keywords": ["에이치엘비", "hlb"]},
    {"name": "알테오젠", "code": "196170", "symbol": "196170.KQ", "market": "KOSDAQ", "keywords": ["alteogen"]},
    {"name": "레인보우로보틱스", "code": "277810", "symbol": "277810.KQ", "market": "KOSDAQ", "keywords": ["레인보우", "로보틱스", "robotics"]},

    {"name": "Apple", "code": "AAPL", "symbol": "AAPL", "market": "NASDAQ", "keywords": ["애플", "apple", "aapl"]},
    {"name": "NVIDIA", "code": "NVDA", "symbol": "NVDA", "market": "NASDAQ", "keywords": ["엔비디아", "nvidia", "nvda", "엔비"]},
    {"name": "Tesla", "code": "TSLA", "symbol": "TSLA", "market": "NASDAQ", "keywords": ["테슬라", "tesla", "tsla"]},
    {"name": "Microsoft", "code": "MSFT", "symbol": "MSFT", "market": "NASDAQ", "keywords": ["마이크로소프트", "msft"]},
    {"name": "Amazon", "code": "AMZN", "symbol": "AMZN", "market": "NASDAQ", "keywords": ["아마존", "amazon"]},
    {"name": "Meta Platforms", "code": "META", "symbol": "META", "market": "NASDAQ", "keywords": ["메타", "페이스북", "facebook"]},
    {"name": "Google Alphabet A", "code": "GOOGL", "symbol": "GOOGL", "market": "NASDAQ", "keywords": ["구글", "알파벳", "google", "alphabet"]},
    {"name": "Broadcom", "code": "AVGO", "symbol": "AVGO", "market": "NASDAQ", "keywords": ["브로드컴", "broadcom"]},
    {"name": "AMD", "code": "AMD", "symbol": "AMD", "market": "NASDAQ", "keywords": ["암드", "amd"]},
    {"name": "Intel", "code": "INTC", "symbol": "INTC", "market": "NASDAQ", "keywords": ["인텔", "intel"]},
    {"name": "Micron", "code": "MU", "symbol": "MU", "market": "NASDAQ", "keywords": ["마이크론", "micron"]},
    {"name": "Palantir", "code": "PLTR", "symbol": "PLTR", "market": "NASDAQ", "keywords": ["팔란티어", "palantir"]},
    {"name": "IonQ", "code": "IONQ", "symbol": "IONQ", "market": "NYSE", "keywords": ["아이온큐", "ionq", "ion"]},

    {"name": "SPDR S&P 500 ETF", "code": "SPY", "symbol": "SPY", "market": "NYSEARCA", "keywords": ["s&p500", "sp500", "snp500", "spy", "에스앤피", "에센피", "s&p 500"]},
    {"name": "Vanguard S&P 500 ETF", "code": "VOO", "symbol": "VOO", "market": "NYSEARCA", "keywords": ["s&p500", "sp500", "voo", "뱅가드", "s&p 500"]},
    {"name": "iShares Core S&P 500 ETF", "code": "IVV", "symbol": "IVV", "market": "NYSEARCA", "keywords": ["s&p500", "sp500", "ivv", "아이셰어즈", "s&p 500"]},
    {"name": "Invesco QQQ Trust", "code": "QQQ", "symbol": "QQQ", "market": "NASDAQ", "keywords": ["나스닥100", "nasdaq100", "qqq", "나스닥 etf"]},
    {"name": "Invesco NASDAQ 100 ETF", "code": "QQQM", "symbol": "QQQM", "market": "NASDAQ", "keywords": ["나스닥100", "nasdaq100", "qqqm"]},
    {"name": "SPDR Dow Jones ETF", "code": "DIA", "symbol": "DIA", "market": "NYSEARCA", "keywords": ["다우", "dow", "dia"]},
    {"name": "iShares Russell 2000 ETF", "code": "IWM", "symbol": "IWM", "market": "NYSEARCA", "keywords": ["러셀2000", "russell", "iwm"]},
    {"name": "Schwab US Dividend Equity ETF", "code": "SCHD", "symbol": "SCHD", "market": "NYSEARCA", "keywords": ["schd", "배당", "dividend"]},
    {"name": "Direxion Daily Semiconductor Bull 3X", "code": "SOXL", "symbol": "SOXL", "market": "NYSEARCA", "keywords": ["soxl", "반도체3배", "semiconductor"]},
    {"name": "iShares Semiconductor ETF", "code": "SOXX", "symbol": "SOXX", "market": "NASDAQ", "keywords": ["soxx", "반도체", "semiconductor"]},
    {"name": "VanEck Semiconductor ETF", "code": "SMH", "symbol": "SMH", "market": "NASDAQ", "keywords": ["smh", "반도체", "엔비디아 etf"]},
    {"name": "ARK Innovation ETF", "code": "ARKK", "symbol": "ARKK", "market": "NYSEARCA", "keywords": ["arkk", "아크", "innovation"]},
]

TOP5_UNIVERSE = [
    {"name": "SK하이닉스", "code": "000660", "symbol": "000660.KS", "market": "KOSPI"},
    {"name": "삼성전자", "code": "005930", "symbol": "005930.KS", "market": "KOSPI"},
    {"name": "현대차", "code": "005380", "symbol": "005380.KS", "market": "KOSPI"},
    {"name": "기아", "code": "000270", "symbol": "000270.KS", "market": "KOSPI"},
    {"name": "NAVER", "code": "035420", "symbol": "035420.KS", "market": "KOSPI"},
    {"name": "카카오", "code": "035720", "symbol": "035720.KS", "market": "KOSPI"},
    {"name": "한화에어로스페이스", "code": "012450", "symbol": "012450.KS", "market": "KOSPI"},
    {"name": "한미반도체", "code": "042700", "symbol": "042700.KS", "market": "KOSPI"},
    {"name": "에코프로비엠", "code": "247540", "symbol": "247540.KQ", "market": "KOSDAQ"},
    {"name": "Apple", "code": "AAPL", "symbol": "AAPL", "market": "NASDAQ"},
    {"name": "NVIDIA", "code": "NVDA", "symbol": "NVDA", "market": "NASDAQ"},
    {"name": "Tesla", "code": "TSLA", "symbol": "TSLA", "market": "NASDAQ"},
    {"name": "Microsoft", "code": "MSFT", "symbol": "MSFT", "market": "NASDAQ"},
    {"name": "SPDR S&P 500 ETF", "code": "SPY", "symbol": "SPY", "market": "NYSEARCA"},
    {"name": "Invesco QQQ Trust", "code": "QQQ", "symbol": "QQQ", "market": "NASDAQ"},
    {"name": "VanEck Semiconductor ETF", "code": "SMH", "symbol": "SMH", "market": "NASDAQ"},
]


@app.route("/")
def index():
    return send_from_directory(".", HTML_FILE)


@app.route("/wealthgrow_agent.html")
def html():
    return send_from_directory(".", HTML_FILE)


@app.route("/api/proxy")
def proxy():
    url = request.args.get("url")

    if not url:
        return Response("Missing url", status=400)

    if not any(url.startswith(domain) for domain in ALLOWED_DOMAINS):
        return Response("Blocked domain", status=403)

    try:
        response = requests.get(url, headers=HEADERS, timeout=12)

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get("Content-Type", "application/json")
        )

    except Exception as e:
        return Response(str(e), status=500)


@app.route("/api/search")
def search_stocks():
    keyword = request.args.get("q", "").strip()

    if not keyword:
        return jsonify({"results": []})

    results = []

    results.extend(search_from_master(keyword))

    if is_six_digit_code(keyword):
        results.extend(search_korean_code(keyword))

    results.extend(search_from_yahoo(keyword))

    cleaned = deduplicate_results(results)

    return jsonify({
        "query": keyword,
        "results": cleaned[:15]
    })


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


@app.route("/api/top5")
def top5():
    today = datetime.now().strftime("%Y-%m-%d")

    if TOP5_CACHE["date"] == today and TOP5_CACHE["data"] is not None:
        return jsonify(TOP5_CACHE["data"])

    analyzed = []

    for stock in TOP5_UNIVERSE:
        try:
            data = analyze_top5_stock(stock)

            if data:
                analyzed.append(data)

        except Exception:
            continue

    undervalued = sorted(
        analyzed,
        key=lambda x: x.get("undervaluedScore", 0),
        reverse=True
    )[:5]

    upside = sorted(
        analyzed,
        key=lambda x: x.get("upsideScore", 0),
        reverse=True
    )[:5]

    result = {
        "updatedAt": today,
        "description": "PER, PBR, 부채비율, EPS 성장률, RSI, 20/60/120일 이동평균, 골든크로스, 모멘텀, 변동성을 종합 반영",
        "undervalued": undervalued,
        "upside": upside
    }

    TOP5_CACHE["date"] = today
    TOP5_CACHE["data"] = result

    return jsonify(result)


def normalize_text(text):
    return str(text or "").lower().replace(" ", "").replace("-", "").replace("_", "").replace("&", "")


def is_six_digit_code(text):
    return text.isdigit() and len(text) == 6


def search_from_master(keyword):
    key = normalize_text(keyword)
    result = []

    for item in SEARCH_MASTER:
        targets = [
            item.get("name"),
            item.get("code"),
            item.get("symbol"),
            item.get("market"),
            *item.get("keywords", [])
        ]

        targets = [normalize_text(v) for v in targets]

        if any(key in target or target in key for target in targets):
            result.append({
                "name": item["name"],
                "code": item["code"],
                "symbol": item["symbol"],
                "market": item["market"],
                "source": "master"
            })

    return result


def search_korean_code(code):
    result = []

    candidates = [
        {"symbol": f"{code}.KS", "market": "KOSPI"},
        {"symbol": f"{code}.KQ", "market": "KOSDAQ"}
    ]

    for candidate in candidates:
        symbol = candidate["symbol"]

        if verify_symbol_has_chart(symbol):
            result.append({
                "name": code,
                "code": code,
                "symbol": symbol,
                "market": candidate["market"],
                "source": "korean-code"
            })

    return result


def search_from_yahoo(keyword):
    result = []

    try:
        encoded = quote(keyword, safe="")
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={encoded}&quotesCount=12&newsCount=0"

        response = requests.get(url, headers=HEADERS, timeout=12)

        if response.status_code != 200:
            return result

        data = response.json()
        quotes = data.get("quotes", [])

        for q in quotes:
            symbol = q.get("symbol")
            name = q.get("shortname") or q.get("longname") or q.get("symbol")
            exchange = q.get("exchDisp") or q.get("exchange") or "GLOBAL"
            quote_type = q.get("quoteType") or ""

            if not symbol:
                continue

            if not is_allowed_quote_type(quote_type):
                continue

            result.append({
                "name": name,
                "code": symbol.replace(".KS", "").replace(".KQ", ""),
                "symbol": symbol,
                "market": exchange,
                "source": "yahoo"
            })

    except Exception:
        return result

    return result


def is_allowed_quote_type(quote_type):
    allowed = [
        "EQUITY",
        "ETF",
        "INDEX",
        "MUTUALFUND"
    ]

    if not quote_type:
        return True

    return quote_type.upper() in allowed


def deduplicate_results(results):
    seen = set()
    cleaned = []

    for item in results:
        symbol = item.get("symbol")

        if not symbol:
            continue

        if symbol in seen:
            continue

        seen.add(symbol)

        cleaned.append({
            "name": item.get("name") or symbol,
            "code": item.get("code") or symbol,
            "symbol": symbol,
            "market": item.get("market") or "GLOBAL",
            "source": item.get("source") or "unknown"
        })

    return cleaned


def verify_symbol_has_chart(symbol):
    try:
        chart = fetch_chart(symbol, range_value="5d", interval="1d")

        if not chart:
            return False

        prices = extract_prices(chart)

        return len(prices) >= 2

    except Exception:
        return False


def analyze_top5_stock(stock):
    symbol = stock["symbol"]

    chart = fetch_chart(symbol, range_value="1y", interval="1d")

    if not chart:
        return None

    prices = extract_prices(chart)

    if len(prices) < 60:
        return None

    current = prices[-1]
    ma20 = moving_average(prices, 20)
    ma60 = moving_average(prices, 60)
    ma120 = moving_average(prices, 120)
    rsi = calculate_rsi(prices, 14)

    momentum20 = percent_change(prices, 20)
    momentum60 = percent_change(prices, 60)

    high52 = max(prices)
    drawdown_from_high = (current - high52) / high52 * 100

    returns = []

    for i in range(1, len(prices)):
        if prices[i - 1] != 0:
            returns.append((prices[i] - prices[i - 1]) / prices[i - 1])

    volatility = std_dev(returns) * math.sqrt(252) if returns else 0

    golden_cross = ma20 > ma60 and ma60 >= ma120 * 0.97

    fundamentals = fetch_fundamentals(symbol)

    per = fundamentals.get("per")
    pbr = fundamentals.get("pbr")
    debt_ratio = fundamentals.get("debtRatio")
    eps_growth = fundamentals.get("epsGrowth")

    undervalued_score = calculate_undervalued_score(
        per=per,
        pbr=pbr,
        debt_ratio=debt_ratio,
        eps_growth=eps_growth,
        rsi=rsi,
        drawdown_from_high=drawdown_from_high,
        momentum20=momentum20,
        momentum60=momentum60,
        golden_cross=golden_cross,
        volatility=volatility
    )

    upside_score = calculate_upside_score(
        per=per,
        pbr=pbr,
        debt_ratio=debt_ratio,
        eps_growth=eps_growth,
        rsi=rsi,
        momentum20=momentum20,
        momentum60=momentum60,
        ma20=ma20,
        ma60=ma60,
        ma120=ma120,
        current=current,
        golden_cross=golden_cross,
        volatility=volatility
    )

    reasons = make_reasons(
        per=per,
        pbr=pbr,
        debt_ratio=debt_ratio,
        eps_growth=eps_growth,
        rsi=rsi,
        momentum20=momentum20,
        momentum60=momentum60,
        drawdown_from_high=drawdown_from_high,
        golden_cross=golden_cross,
        volatility=volatility
    )

    risk_cut_percent = get_top5_risk_cut_percent(upside_score, volatility, rsi)
    risk_cut_price = current * (1 - risk_cut_percent)

    expected_return = get_expected_return(upside_score, undervalued_score, volatility)

    return {
        "name": stock["name"],
        "code": stock["code"],
        "symbol": stock["symbol"],
        "market": stock["market"],
        "currentPrice": round(current, 2),
        "riskCutPrice": round(risk_cut_price, 2),
        "expectedDays": "20거래일 기준",
        "expectedReturn": expected_return,
        "undervaluedScore": undervalued_score,
        "upsideScore": upside_score,
        "per": format_optional_number(per),
        "pbr": format_optional_number(pbr),
        "debtRatio": format_optional_number(debt_ratio),
        "epsGrowth": format_optional_number(eps_growth),
        "rsi": round(rsi, 1),
        "momentum20": round(momentum20, 1),
        "momentum60": round(momentum60, 1),
        "goldenCross": golden_cross,
        "reasons": reasons
    }


def fetch_chart(symbol, range_value="1y", interval="1d"):
    try:
        encoded_symbol = quote(symbol, safe="")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}?range={range_value}&interval={interval}"

        response = requests.get(url, headers=HEADERS, timeout=12)

        if response.status_code != 200:
            return None

        json_data = response.json()
        result = json_data.get("chart", {}).get("result", [])

        if not result:
            return None

        return result[0]

    except Exception:
        return None


def fetch_fundamentals(symbol):
    result = {
        "per": None,
        "pbr": None,
        "debtRatio": None,
        "epsGrowth": None
    }

    try:
        encoded_symbol = quote(symbol, safe="")
        modules = "summaryDetail,defaultKeyStatistics,financialData,earningsTrend"
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{encoded_symbol}?modules={modules}"

        response = requests.get(url, headers=HEADERS, timeout=12)

        if response.status_code != 200:
            return result

        json_data = response.json()
        quote_result = json_data.get("quoteSummary", {}).get("result", [])

        if not quote_result:
            return result

        data = quote_result[0]

        summary_detail = data.get("summaryDetail", {})
        default_key = data.get("defaultKeyStatistics", {})
        financial_data = data.get("financialData", {})
        earnings_trend = data.get("earningsTrend", {})

        per = extract_raw(summary_detail.get("trailingPE"))
        if per is None:
            per = extract_raw(default_key.get("trailingPE"))

        pbr = extract_raw(default_key.get("priceToBook"))
        debt_ratio = extract_raw(financial_data.get("debtToEquity"))

        eps_growth = None
        trend = earnings_trend.get("trend", [])

        if trend:
            for item in trend:
                period = item.get("period")

                if period in ["+1y", "0y", "+1q"]:
                    growth = extract_raw(item.get("growth"))

                    if growth is not None:
                        eps_growth = growth * 100
                        break

        result = {
            "per": per,
            "pbr": pbr,
            "debtRatio": debt_ratio,
            "epsGrowth": eps_growth
        }

        return result

    except Exception:
        return result


def extract_raw(value):
    if isinstance(value, dict):
        raw = value.get("raw")

        if isinstance(raw, (int, float)):
            return raw

    if isinstance(value, (int, float)):
        return value

    return None


def extract_prices(chart):
    try:
        quote_data = chart.get("indicators", {}).get("quote", [])

        if not quote_data:
            return []

        closes = quote_data[0].get("close", [])

        prices = []

        for value in closes:
            if value is not None:
                prices.append(float(value))

        return prices

    except Exception:
        return []


def get_yahoo_chart_simple(symbol):
    try:
        chart = fetch_chart(symbol, range_value="5d", interval="1d")

        if not chart:
            return None

        prices = extract_prices(chart)

        if len(prices) < 2:
            return None

        current = prices[-1]
        previous = prices[-2]
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


def moving_average(values, period):
    if not values:
        return 0

    p = min(len(values), period)
    sliced = values[-p:]

    return sum(sliced) / len(sliced)


def percent_change(values, days):
    if len(values) <= days:
        return 0

    current = values[-1]
    past = values[-1 - days]

    if past == 0:
        return 0

    return (current - past) / past * 100


def calculate_rsi(values, period=14):
    if len(values) <= period:
        return 50

    recent = values[-period - 1:]

    gains = 0
    losses = 0

    for i in range(1, len(recent)):
        diff = recent[i] - recent[i - 1]

        if diff >= 0:
            gains += diff
        else:
            losses += abs(diff)

    if losses == 0:
        return 100

    rs = gains / losses

    return 100 - 100 / (1 + rs)


def std_dev(values):
    if not values:
        return 0

    avg = sum(values) / len(values)
    variance = sum((value - avg) ** 2 for value in values) / len(values)

    return math.sqrt(variance)


def calculate_undervalued_score(
    per,
    pbr,
    debt_ratio,
    eps_growth,
    rsi,
    drawdown_from_high,
    momentum20,
    momentum60,
    golden_cross,
    volatility
):
    score = 50

    if per is not None:
        if per <= 8:
            score += 18
        elif per <= 15:
            score += 13
        elif per <= 25:
            score += 6
        elif per >= 50:
            score -= 10

    if pbr is not None:
        if pbr <= 1:
            score += 16
        elif pbr <= 2:
            score += 10
        elif pbr <= 4:
            score += 4
        elif pbr >= 8:
            score -= 8

    if debt_ratio is not None:
        if debt_ratio <= 80:
            score += 10
        elif debt_ratio <= 150:
            score += 4
        elif debt_ratio >= 250:
            score -= 10

    if eps_growth is not None:
        if eps_growth >= 25:
            score += 12
        elif eps_growth >= 10:
            score += 7
        elif eps_growth < 0:
            score -= 8

    if 35 <= rsi <= 60:
        score += 10
    elif rsi > 75:
        score -= 8

    if drawdown_from_high <= -20 and momentum20 > 0:
        score += 8

    if momentum60 > 0:
        score += 5

    if golden_cross:
        score += 6

    if volatility > 0.65:
        score -= 8
    elif volatility < 0.35:
        score += 5

    return max(0, min(100, round(score)))


def calculate_upside_score(
    per,
    pbr,
    debt_ratio,
    eps_growth,
    rsi,
    momentum20,
    momentum60,
    ma20,
    ma60,
    ma120,
    current,
    golden_cross,
    volatility
):
    score = 50

    if current > ma20:
        score += 8
    else:
        score -= 5

    if ma20 > ma60:
        score += 10
    else:
        score -= 5

    if ma60 > ma120:
        score += 8

    if golden_cross:
        score += 12

    if momentum20 > 0:
        score += 8
    else:
        score -= 6

    if momentum60 > 0:
        score += 8
    else:
        score -= 4

    if 45 <= rsi <= 68:
        score += 10
    elif 68 < rsi <= 78:
        score += 3
    elif rsi > 78:
        score -= 10
    elif rsi < 30:
        score -= 7

    if eps_growth is not None:
        if eps_growth >= 25:
            score += 12
        elif eps_growth >= 10:
            score += 7
        elif eps_growth < 0:
            score -= 8

    if per is not None:
        if per <= 25:
            score += 5
        elif per >= 70:
            score -= 8

    if pbr is not None:
        if pbr <= 5:
            score += 4
        elif pbr >= 12:
            score -= 8

    if debt_ratio is not None:
        if debt_ratio <= 150:
            score += 4
        elif debt_ratio >= 300:
            score -= 8

    if volatility > 0.70:
        score -= 10
    elif volatility < 0.45:
        score += 5

    return max(0, min(100, round(score)))


def make_reasons(
    per,
    pbr,
    debt_ratio,
    eps_growth,
    rsi,
    momentum20,
    momentum60,
    drawdown_from_high,
    golden_cross,
    volatility
):
    reasons = []

    if per is not None:
        reasons.append(f"PER {per:.1f}")

    if pbr is not None:
        reasons.append(f"PBR {pbr:.1f}")

    if debt_ratio is not None:
        reasons.append(f"부채비율 {debt_ratio:.0f}%")

    if eps_growth is not None:
        reasons.append(f"EPS 성장률 {eps_growth:.1f}%")

    reasons.append(f"RSI {rsi:.1f}")
    reasons.append(f"20일 모멘텀 {momentum20:.1f}%")
    reasons.append(f"60일 모멘텀 {momentum60:.1f}%")

    if golden_cross:
        reasons.append("골든크로스 확인")
    else:
        reasons.append("골든크로스 미확인")

    if drawdown_from_high <= -20:
        reasons.append("52주 고점 대비 조정")

    reasons.append(f"변동성 {volatility * 100:.1f}%")

    return reasons[:6]


def get_top5_risk_cut_percent(score, volatility, rsi):
    risk = 0.08

    if score >= 80:
        risk = 0.10
    elif score >= 65:
        risk = 0.08
    else:
        risk = 0.06

    if volatility > 0.60:
        risk *= 0.8

    if rsi > 75:
        risk *= 0.85

    return risk


def get_expected_return(upside_score, undervalued_score, volatility):
    base_score = upside_score * 0.65 + undervalued_score * 0.35

    if base_score >= 85:
        expected = 8.5
    elif base_score >= 75:
        expected = 6.2
    elif base_score >= 65:
        expected = 4.0
    elif base_score >= 55:
        expected = 2.0
    else:
        expected = -1.5

    if volatility > 0.65:
        expected -= 1.2

    return round(expected, 1)


def format_optional_number(value):
    if value is None:
        return None

    return round(value, 2)


@app.route("/favicon.ico")
def favicon():
    return Response(status=204)


@app.route("/<path:path>")
def catch_all(path):
    if path.startswith("api/"):
        return Response("API Not Found", status=404)

    return send_from_directory(".", HTML_FILE)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
