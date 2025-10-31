import httpx
from datetime import datetime
from main.logic.models import arbitrage_decision
from main.config import settings


def _fmt(n: float) -> str:
    return f"{n:,.2f}"


def build_message(decision: arbitrage_decision, pair: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"Time: {now}\n"
        f"Pair: {pair}\n"
        f"Buy @ {decision.buy_exchange}: {_fmt(decision.buy_price)} USDT\n"
        f"Sell @ {decision.sell_exchange}: {_fmt(decision.sell_price)} USDT\n"
        f"Diff: {_fmt(decision.diff)}  ({decision.pct:.3f}%)\n\n"
        f"Rule: threshold={settings.threshold_pct}% | min_vol={_fmt(settings.min_trade_usdt)} USDT"
    )


async def _post_json(url: str, payload: dict) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json=payload)
            return r.status_code == 200
    except Exception as e:
        print(f"POST failed to {url}: {e}")
        return False


async def _send_telegram(text: str) -> bool:
    if not settings.bot_token or not settings.chat_id:
        return False
    url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
    payload = {"chat_id": settings.chat_id, "text": text}
    return await _post_json(url, payload)


async def _send_bale(text: str) -> bool:
    if not settings.bale_bot_token or not settings.bale_chat_id:
        return False
    url = f"https://tapi.bale.ai/bot{settings.bale_bot_token}/sendMessage"
    payload = {"chat_id": settings.bale_chat_id, "text": text}
    return await _post_json(url, payload)


async def send_opportunity(decision: arbitrage_decision, pair: str) -> bool:
    text = build_message(decision, pair)
    ok_tg = await _send_telegram(text)
    ok_bale = await _send_bale(text)
    return bool(ok_tg or ok_bale)

