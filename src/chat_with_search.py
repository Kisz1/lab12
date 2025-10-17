# utils/conversion_tools.py
from __future__ import annotations
import time
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
    "usd": "USD", "eur": "EUR", "gbp": "GBP", "jpy": "JPY", "thb": "THB",
    "aud": "AUD", "cad": "CAD", "chf": "CHF", "cny": "CNY", "hkd": "HKD",
    "sgd": "SGD", "inr": "INR", "krw": "KRW", "vnd": "VND", "idr": "IDR",
    "myr": "MYR", "php": "PHP", "twd": "TWD", "nzd": "NZD", "sek": "SEK",
    "nok": "NOK", "dkk": "DKK", "mxn": "MXN", "zar": "ZAR", "try": "TRY",
    # Crypto (extend as needed)
    "btc": "BTC", "bitcoin": "BTC",
}

# CoinGecko id map (extend if needed)
_CG_IDS = {"BTC": "bitcoin"}

def _safe_float(x: str) -> Optional[float]:
    try:
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
        base = base.upper()
        cached = self._fiat_cache.get(base)
        if cached and _now() - cached["t"] < self.ttl:
            return cached["rates"]
        resp = requests.get(_FIAT_API, params={"base": base}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # exchangerate.host returns {"success": True, "base": "...", "rates": {...}} or sometimes without "success"
        rates = data.get("rates")
        if not isinstance(rates, dict):
            raise RuntimeError(f"exchangerate.host error/format: {data}")
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
