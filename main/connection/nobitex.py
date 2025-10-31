import time
import httpx
from typing import Optional
from main.logic.models import prices_data
from main.flow.metrics import calculate_latency, set_request_ok, set_request_error

NOBITEX_NAME = "Nobitex"
PAIR_IN = "BTCUSDT"
PAIR_OUT = "btc-usdt"
API_STATS = "https://apiv2.nobitex.ir/market/stats?symbol=" + PAIR_OUT


async def fetch_price_btcusdt() -> prices_data:
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(API_STATS)
            latency = time.perf_counter() - start
            calculate_latency(NOBITEX_NAME, latency)

            if r.status_code != 200:
                set_request_error(NOBITEX_NAME)
                return prices_data(
                    exchange_name=NOBITEX_NAME, our_symbol=PAIR_IN, exchange_symbol=PAIR_OUT,
                    last_price=0.0, ok=False, error=f"HTTP {r.status_code}"
                )

            data = r.json()
            # مسیر متداول: data["stats"]["btc-usdt"]["latest"] یا "last"
            stats = data.get("stats", {}).get(PAIR_OUT, {})
            last_str: Optional[str] = stats.get("latest") or stats.get("last")
            if last_str is None:
                set_request_error(NOBITEX_NAME)
                return prices_data(
                    exchange_name=NOBITEX_NAME, our_symbol=PAIR_IN, exchange_symbol=PAIR_OUT,
                    last_price=0.0, ok=False, error="missing latest/last"
                )

            last_price = float(last_str)
            ts = data.get("lastUpdate") or None

            set_request_ok(NOBITEX_NAME)
            return prices_data(
                exchange_name=NOBITEX_NAME,
                our_symbol=PAIR_IN,
                exchange_symbol=PAIR_OUT,
                last_price=last_price,
                last_update_time=ts,
                ok=True
            )
    except Exception as e:
        latency = time.perf_counter() - start
        calculate_latency(NOBITEX_NAME, latency)
        set_request_error(NOBITEX_NAME)
        return prices_data(
            exchange_name=NOBITEX_NAME, our_symbol=PAIR_IN, exchange_symbol=PAIR_OUT,
            last_price=0.0, ok=False, error=str(e)
        )
