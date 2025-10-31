import asyncio
from typing import Optional
from main.config import settings
from main.connection.nobitex import fetch_price_btcusdt as nobitex_price
from main.connection.wallex import fetch_price_btcusdt as wallex_price
from main.logic.arbitrage import decide
from main.flow.metrics import set_spread, opportunity_found
from main.services.server import save_tick, save_opportunity
import time

PAIR = "BTCUSDT"

_last_alert_key: Optional[str] = None
_last_sent_ts: float = 0.0


def _alert_key(buy: str, sell: str, diff: float) -> str:
    return f"{buy}->{sell}:{round(diff, 2)}"


async def run_loop():
    global _last_alert_key, _last_sent_ts
    backoff_nobitex = 0
    backoff_wallex = 0

    while True:
        await asyncio.sleep(settings.poll_interval_sec)
        if backoff_nobitex <= 0:
            get_nob = nobitex_price()
        else:
            get_nob = None

        if backoff_wallex <= 0:
            get_wal = wallex_price()
        else:
            get_wal = None

        nob = await get_nob if get_nob else None
        wal = await get_wal if get_wal else None

        backoff_nob = max(0, backoff_nobitex - settings.poll_interval_sec)
        backoff_wallex = max(0, backoff_wallex - settings.poll_interval_sec)

        if nob and not nob.ok:
            backoff_nobitex = max(backoff_nobitex, 30)
        if wal and not wal.ok:
            backoff_wal = max(backoff_wallex, 30)

        if not (nob and wal):
            continue

        await save_tick(nob.exchange_name, PAIR, nob.last_price)
        await save_tick(wal.exchange_name, PAIR, wal.last_price)

        decision = decide(nob, wal, settings.threshold_pct, settings.min_trade_usdt)
        if decision.is_opportunity:
            _ = await save_opportunity(
                PAIR,
                decision.buy_exchange,
                decision.sell_exchange,
                decision.diff,
                decision.pct,
                getattr(decision, "est_profit_usd", None)
            )

        set_spread(PAIR, decision.diff, decision.pct)

        if decision.is_opportunity:
            key = _alert_key(decision.buy_exchange, decision.sell_exchange, decision.diff)
            now = time.time()
            cooldown_ok = (now - _last_sent_ts) >= settings.notify_cooldown_sec
            key_changed = (key != _last_alert_key)

            # pct_changed = abs(decision.pct - _last_pct) >= settings.notify_min_pct_delta
            #  cooldown_ok and (key_changed or pct_changed)

            if cooldown_ok and key_changed:
                from main.flow.notifier import send_opportunity
                ok = await send_opportunity(decision, PAIR)
                if ok:
                    opportunity_found(PAIR)
                    _last_alert_key = key
                    _last_sent_ts = now
            # if key != _last_alert_key:
            #     from main.flow.notifier import send_opportunity
            #     ok = await send_opportunity(decision, PAIR)
            #     if ok:
            #         opportunity_found(PAIR)
            #         _last_alert_key = key
