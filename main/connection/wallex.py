import time
import httpx
from typing import Optional
from main.logic.models import prices_data
from main.flow.metrics import calculate_latency, set_request_ok, set_request_error

WALLEX_NAME = "Wallex"
PAIR_IN = "BTCUSDT"
PAIR_OUT = "BTCUSDT"

API_MARKETS = "https://api.wallex.ir/v1/markets"


async def fetch_price_btcusdt() -> prices_data:
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(API_MARKETS)
            latency = time.perf_counter() - start
            calculate_latency(WALLEX_NAME, latency)

            if r.status_code != 200:
                set_request_error(WALLEX_NAME)
                return prices_data(
                    exchange_name=WALLEX_NAME, our_symbol=PAIR_IN, exchange_symbol=PAIR_OUT,
                    last_price=0.0, ok=False, error=f"HTTP {r.status_code}"
                )

            data = r.json()
            symbols = data.get("result", {}).get("symbols", {})
            stats = symbols.get(PAIR_OUT, {}).get("stats", {})
            last_str: Optional[str] = stats.get("lastPrice")
            if last_str is None:
                set_request_error(WALLEX_NAME)
                return prices_data(
                    exchange_name=WALLEX_NAME, our_symbol=PAIR_IN, exchange_symbol=PAIR_OUT,
                    last_price=0.0, ok=False, error="missing lastPrice"
                )

            last_price = float(last_str)
            ts = None  # در بازار‌ها معمولا زمان کلی میاد، اگر needed بعدا اضافه کن

            set_request_ok(WALLEX_NAME)
            return prices_data(
                exchange_name=WALLEX_NAME,
                our_symbol=PAIR_IN,
                exchange_symbol=PAIR_OUT,
                last_price=last_price,
                last_update_time=ts,
                ok=True
            )
    except Exception as e:
        latency = time.perf_counter() - start
        calculate_latency(WALLEX_NAME, latency)
        set_request_error(WALLEX_NAME)
        return prices_data(
            exchange_name=WALLEX_NAME, our_symbol=PAIR_IN, exchange_symbol=PAIR_OUT,
            last_price=0.0, ok=False, error=str(e)
        )
