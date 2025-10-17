# utils/conversion_tools.py
from __future__ import annotations
import os
import time
import math
import re
import requests
from typing import Tuple, Optional, Dict

"""
CurrencyTool
- Fiat rates via exchangerate.host (no API key required)
- BTC rates via CoinGecko (no API key required)
- Light in-memory caching with TTL to avoid rate limits
"""

_FIAT_API = "https://api.exchangerate.host/latest"
_CG_SIMPLE_PRICE = "https://api.coingecko.com/api/v3/simple/price"

# Common symbols map
_SYMBOL_TO_CODE = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "฿": "THB",
}

# Normalize aliases
_ALIAS_TO_CODE = {
    "usd": "USD", "usdt": "USDT",  # USDT not supported for fiat API; here we stick to fiat codes
    "eur": "EUR",
    "gbp": "GBP",
    "jpy": "JPY",
    "thb": "THB",
    "aud": "AUD",
    "cad": "CAD",
    "chf": "CHF",
    "cny": "CNY",
    "hkd": "HKD",
    "sgd": "SGD",
    "inr": "INR",
    "krw": "KRW",
    "vnd": "VND",
    "idr": "IDR",
    "myr": "MYR",
    "php": "PHP",
    "twd": "TWD",
    "nzd": "NZD",
    "sek": "SEK",
    "nok": "NOK",
    "dkk": "DKK",
    "mxn": "MXN",
    "zar": "ZAR",
    "try": "TRY",
    # Crypto (only mapping BTC here per assignment)
    "btc": "BTC",
    "bitcoin": "BTC",
}

# CoinGecko id map (expand if needed)
_CG_IDS = {
    "BTC": "bitcoin",
}

def _safe_float(x: str) -> Optional[float]:
    try:
        # allow commas in numbers: "1,234.56"
        return float(x.replace(",", ""))
    except Exception:
        return None

def _now() -> float:
    return time.time()

class CurrencyTool:
    def __init__(self, default_target: str = "THB", ttl_seconds: int = 300):
        """
        default_target: used when user asks "exchange rate for Bitcoin?" without target currency
        ttl_seconds: cache TTL for API hits (default 5 min)
        """
        self.default_target = default_target.upper()
        self.ttl = ttl_seconds
        self._fiat_cache: Dict[str, Dict] = {}      # key=f"{base}", value={"t":ts,"rates":{...}}
        self._crypto_cache: Dict[str, Dict] = {}    # key=f"{coin_id}|{vs}", value={"t":ts,"price":float}

    # ---------- Normalization ----------

    def normalize_code(self, token: str) -> Optional[str]:
        if not token:
            return None
        token = token.strip()
        if token in _SYMBOL_TO_CODE:
            return _SYMBOL_TO_CODE[token]
        lo = token.lower()
        if lo in _ALIAS_TO_CODE:
            return _ALIAS_TO_CODE[lo]
        if len(token) == 3 and token.isalpha():
            return token.upper()
        return None

    # ---------- Fiat rates ----------

    def _fetch_fiat_rates(self, base: str) -> Dict[str, float]:
        # cache by base
        base = base.upper()
        cached = self._fiat_cache.get(base)
        if cached and _now() - cached["t"] < self.ttl:
            return cached["rates"]
        resp = requests.get(_FIAT_API, params={"base": base}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success", True) and "rates" not in data:
            raise RuntimeError(f"exchangerate.host error: {data}")
        rates = data["rates"]
        # store
        self._fiat_cache[base] = {"t": _now(), "rates": rates}
        return rates

    def get_fiat_rate(self, base: str, target: str) -> float:
        base, target = base.upper(), target.upper()
        if base == target:
            return 1.0
        rates = self._fetch_fiat_rates(base)
        if target not in rates:
            # Fallback via USD triangulation if target missing
            if "USD" in rates:
                usd_rate = rates["USD"]       # 1 base = usd_rate USD
                # get target vs USD
                rates_usd = self._fetch_fiat_rates("USD")
                if target not in rates_usd:
                    raise ValueError(f"Unsupported target currency: {target}")
                return usd_rate * rates_usd[target]  # 1 base = (base->USD) * (USD->target)
            raise ValueError(f"Unsupported target currency: {target}")
        return rates[target]

    # ---------- Crypto (BTC) ----------

    def get_btc_rate(self, vs_code: str) -> float:
        vs_code = vs_code.upper()
        cg_vs = vs_code.lower()
        cg_id = _CG_IDS["BTC"]
        key = f"{cg_id}|{cg_vs}"
        cached = self._crypto_cache.get(key)
        if cached and _now() - cached["t"] < self.ttl:
            return cached["price"]

        resp = requests.get(
            _CG_SIMPLE_PRICE,
            params={"ids": cg_id, "vs_currencies": cg_vs},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        try:
            price = float(data[cg_id][cg_vs])
        except Exception:
            raise RuntimeError(f"CoinGecko response unexpected: {data}")
        self._crypto_cache[key] = {"t": _now(), "price": price}
        return price

    # ---------- Convert ----------

    def convert(self, amount: float, from_code: str, to_code: str) -> Tuple[float, float, str]:
        """
        Returns (converted_amount, rate, source)
        - rate is quoted as: 1 FROM = rate TO
        """
        f, t = self.normalize_code(from_code), self.normalize_code(to_code)
        if not f:
            raise ValueError(f"Unknown source currency: {from_code}")
        if not t:
            raise ValueError(f"Unknown target currency: {to_code}")

        # Handle BTC legs
        if f == "BTC" and t != "BTC":
            rate = self.get_btc_rate(t)  # 1 BTC = rate t
            return amount * rate, rate, "CoinGecko"
        if t == "BTC" and f != "BTC":
            # fiat -> BTC
            price = self.get_btc_rate(f)  # 1 BTC = price f
            rate = 1.0 / price            # 1 f = rate BTC
            return amount * rate, rate, "CoinGecko"
        if f == "BTC" and t == "BTC":
            return amount, 1.0, "CoinGecko"

        # Fiat -> Fiat
        rate = self.get_fiat_rate(f, t)  # 1 f = rate t
        return amount * rate, rate, "exchangerate.host"

    # ---------- Parsing helpers (can be used by chat layer) ----------

    _CONVERT_RE = re.compile(
        r"""
        (?P<verb>convert|แปลง|แลก|exchange)\s*
        (?P<amount>[0-9][0-9,\.]*)\s*
        (?P<src>[A-Za-z]{3}|[$€£¥฿])      # 3-letter or symbol
        (?:\s*(?:to|เป็น|->|in)\s*
            (?P<dst>[A-Za-z]{3}|[$€£¥฿])
        )?
        """,
        re.IGNORECASE | re.VERBOSE
    )

    _RATE_RE = re.compile(
        r"""
        (?:rate|อัตรา|ราคา|exchange\s*rate|เท่าไหร่).*
        (?P<src>btc|bitcoin|[A-Za-z]{3}|[$€£¥฿])
        (?:\s*(?:to|เป็น|in)\s*(?P<dst>[A-Za-z]{3}|[$€£¥฿]))?
        """,
        re.IGNORECASE | re.VERBOSE
    )

    def try_parse(self, text: str) -> Optional[dict]:
        """
        Returns a dict describing the intent if matched:
        - {"type":"convert","amount":float,"from":"USD","to":"THB"}
        - {"type":"rate","from":"BTC","to":"THB"}
        """
        m = self._CONVERT_RE.search(text)
        if m:
            amt = _safe_float(m.group("amount"))
            src = self.normalize_code(m.group("src"))
            dst_raw = m.group("dst")
            dst = self.normalize_code(dst_raw) if dst_raw else None
            if amt is not None and src:
                return {"type": "convert", "amount": amt, "from": src, "to": dst or self.default_target}

        # rate style
        m2 = self._RATE_RE.search(text)
        if m2:
            src = self.normalize_code(m2.group("src"))
            dst_raw = m2.group("dst")
            dst = self.normalize_code(dst_raw) if dst_raw else self.default_target
            if src:
                return {"type": "rate", "from": src, "to": dst}

        # Simpler patterns like "100 USD to EUR"
        simple = re.search(
            r"(?P<amount>[0-9][0-9,\.]*)\s*(?P<src>[A-Za-z]{3}|[$€£¥฿])\s*(?:to|->|เป็น)\s*(?P<dst>[A-Za-z]{3}|[$€£¥฿])",
            text, re.IGNORECASE
        )
        if simple:
            amt = _safe_float(simple.group("amount"))
            src = self.normalize_code(simple.group("src"))
            dst = self.normalize_code(simple.group("dst"))
            if amt is not None and src and dst:
                return {"type": "convert", "amount": amt, "from": src, "to": dst}

        return None

    def render_result(self, payload: dict) -> str:
        """
        Pretty text block for injecting into LLM prompt or direct display.
        """
        if payload.get("type") == "convert":
            amount, f, t = payload["amount"], payload["from"], payload["to"]
            converted, rate, source = self.convert(amount, f, t)
            return (
                f"Live FX (source: {source}): 1 {f} = {rate:,.6f} {t}\n"
                f"{amount:,.4f} {f} = {converted:,.4f} {t}"
            )
        elif payload.get("type") == "rate":
            f, t = payload["from"], payload["to"]
            # compute unit rate only
            converted, rate, source = self.convert(1.0, f, t)
            return f"Live FX (source: {source}): 1 {f} = {rate:,.6f} {t}"
        return "No conversion executed."
