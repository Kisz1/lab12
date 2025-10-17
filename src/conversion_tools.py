import os
import re
import math
import time
import requests
from typing import Optional, Dict, Any, Tuple

__all__ = [
    "should_use_conversion",
    "parse_currency_query",
    "perform_conversion",
    "format_conversion_block",
    "get_resolution_trace",
    "reset_resolution_trace",
]

_RESOLUTION_TRACE: list[str] = []

def reset_resolution_trace() -> None:
    _RESOLUTION_TRACE.clear()

def _t(msg: str) -> None:
    _RESOLUTION_TRACE.append(msg)

def get_resolution_trace() -> str:
    return "\n".join(_RESOLUTION_TRACE)

EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY", "").strip()
EXR_BASE = "https://v6.exchangerate-api.com/v6"
COINGECKO_SIMPLE_PRICE = "https://api.coingecko.com/api/v3/simple/price"

ALIASES = {
    "dollar": "USD", "usd": "USD", "$": "USD",
    "euro": "EUR",  "eur": "EUR", "€": "EUR",
    "baht": "THB",  "thb": "THB", "฿": "THB",
    "pound": "GBP", "gbp": "GBP", "£": "GBP",
    "yen": "JPY",   "jpy": "JPY", "¥": "JPY",
    "yuan": "CNY",  "cny": "CNY",
    "rupee": "INR", "inr": "INR", "₹": "INR",
    "won": "KRW",   "krw": "KRW", "₩": "KRW",
    "dong": "VND",  "vnd": "VND", "₫": "VND",
    "ringgit": "MYR","myr":"MYR",
    "peso": "PHP",  "php": "PHP",
    "franc": "CHF", "chf": "CHF",
    "canadian dollar": "CAD", "cad": "CAD",
    "australian dollar": "AUD", "aud": "AUD",
    "singapore dollar": "SGD", "sgd": "SGD",
    "bitcoin": "BTC", "btc": "BTC",
}

FIAT = {
    "USD","EUR","THB","GBP","JPY","CNY","INR","KRW","VND","MYR","PHP",
    "CHF","CAD","AUD","SGD","HKD","IDR","NZD","SEK","NOK","DKK"
}

NUM_RE = r"(?P<amt>[0-9]+(?:[.,][0-9]+)?)"
CURR_RE = r"(?P<src>[A-Za-z$€฿£¥₹₩₫ ]{1,20})\s*(?:to|in|→|=|->|⇒)\s*(?P<dst>[A-Za-z$€฿£¥₹₩₫ ]{1,20})"
CONVERT_PATTERNS = [
    re.compile(rf"(?:convert|exchange)\s+{NUM_RE}\s+(?P<src>[A-Za-z$€฿£¥₹₩₫ ]+)\s+(?:to|in)\s+(?P<dst>[A-Za-z$€฿£¥₹₩₫ ]+)", re.I),
    re.compile(rf"{NUM_RE}\s+(?P<src>[A-Za-z$€฿£¥₹₩₫ ]+)\s+(?:to|in)\s+(?P<dst>[A-Za-z$€฿£¥₹₩₫ ]+)", re.I),
    re.compile(rf"rate\s+for\s+{CURR_RE}", re.I),
    re.compile(rf"exchange\s+rate\s+{CURR_RE}", re.I),
    re.compile(rf"(?P<src>btc|bitcoin)\s+price(?:\s+in\s+(?P<dst>[A-Za-z]+))?", re.I),
    re.compile(rf"what(?:'s|\s+is)?\s+the\s+(?:current\s+)?(exchange\s+)?rate\s+for\s+(?P<src>btc|bitcoin)", re.I),
    re.compile(rf"(?P<src>[A-Za-z$€฿£¥₹₩₫ ]+)\s+(?:to|in)\s+(?P<dst>[A-Za-z$€฿£¥₹₩₫ ]+)", re.I),
]

def _norm_code(raw: str):
    s = raw.strip().lower()
    s = s.replace(".", "")
    if s in ALIASES:
        return ALIASES[s]
    s = s.strip("$€฿£¥₹₩₫")
    if s in ALIASES:
        return ALIASES[s]
    if len(s) == 3 and s.isalpha():
        return s.upper()
    return None

def _parse_amount(text: str):
    m = re.search(NUM_RE, text.replace(",", ""), flags=re.I)
    if not m:
        return None
    try:
        return float(m.group("amt"))
    except ValueError:
        return None

def should_use_conversion(text: str):
    tl = text.lower()
    triggers = [
        "convert ", "exchange ", "exchange rate", "rate for", "price of",
        " usd", " eur", " thb", " jpy", " cny", " inr", " gbp", " btc", " bitcoin",
        " to thb", " to usd", " to eur", " to btc", "$", "€", "฿", "£", "¥", "₹", "₩", "₫"
    ]
    return any(t in tl for t in triggers)

def parse_currency_query(text: str) -> Optional[Dict[str, Any]]:
    reset_resolution_trace()
    _t(f"Parsing query: {text!r}")
    for p in CONVERT_PATTERNS:
        m = p.search(text)
        if not m:
            continue
        amt = _parse_amount(text)
        src_raw = m.groupdict().get("src")
        dst_raw = m.groupdict().get("dst")
        src = _norm_code(src_raw) if src_raw else None
        dst = _norm_code(dst_raw) if dst_raw else None

        if src in {"BTC"} and not dst:
            dst = "USD"

        if (src and dst) and amt is None:
            amt = 1.0

        if src and (dst or src == "BTC"):
            _t(f"Detected src={src}, dst={dst}, amt={amt}")
            return {"amount": amt, "src": src, "dst": dst}
    _t("No currency pattern matched.")
    return None

def _fetch_fiat_rate(src: str, dst: str):
    if not EXCHANGERATE_API_KEY:
        raise RuntimeError("Missing EXCHANGERATE_API_KEY in environment.")
    if src == dst:
        return 1.0, "EXR (pair, same-currency)"

    url = f"{EXR_BASE}/{EXCHANGERATE_API_KEY}/pair/{src}/{dst}"
    _t(f"GET {url}")
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("result") != "success":
        raise RuntimeError(f"ExchangeRate-API error: {data}")
    rate = float(data["conversion_rate"])
    return rate, "ExchangeRate-API"

def _fetch_btc_to_fiat(dst: str):
    params = {"ids": "bitcoin", "vs_currencies": dst.lower()}
    _t(f"GET {COINGECKO_SIMPLE_PRICE} {params}")
    r = requests.get(COINGECKO_SIMPLE_PRICE, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    val = data.get("bitcoin", {}).get(dst.lower())
    if val is None:
        raise RuntimeError(f"CoinGecko: no BTC->{dst} price")
    return float(val), "CoinGecko"

def _fetch_rate(src: str, dst: str):
    if src == "BTC" and (dst and dst in FIAT):
        return _fetch_btc_to_fiat(dst)
    if src in FIAT and dst in FIAT:
        return _fetch_fiat_rate(src, dst)
    raise RuntimeError(f"Unsupported currency pair {src}->{dst}")

def perform_conversion(amount: Optional[float], src: str, dst: str):
    _t(f"Performing conversion amount={amount} src={src} dst={dst}")
    if not dst:
        # If user asked just for a currency's "rate", define sensible default
        dst = "USD" if src == "BTC" else "THB"
        _t(f"No dst provided; default dst={dst}")

    rate, source = _fetch_rate(src, dst)
    if amount is None:
        amount = 1.0
    converted = rate * float(amount)

    def _smart_round(x: float) -> float:
        if x == 0:
            return 0.0
        mags = max(-6, min(6, int(math.floor(math.log10(abs(x))))))
        sig = 6 - mags
        return float(f"{x:.{max(2, min(6, sig))}f}")

    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    res = {
        "amount": float(amount),
        "src": src,
        "dst": dst,
        "rate": float(rate),
        "converted_amount": _smart_round(converted),
        "source": source,
        "timestamp": ts,
        "normalized_query": f"{amount} {src} -> {dst}",
    }
    _t(f"Result: {res}")
    return res

def format_conversion_block(res: Dict[str, Any]):
    return (
        "### Currency Conversion (tool)\n"
        f"- Normalized: {res['normalized_query']}\n"
        f"- Rate: 1 {res['src']} = {res['rate']} {res['dst']}\n"
        f"- Amount: {res['amount']} {res['src']} → {res['converted_amount']} {res['dst']}\n"
        f"- Source: {res['source']} · {res['timestamp']}\n"
    )