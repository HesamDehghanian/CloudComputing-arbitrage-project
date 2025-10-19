# import httpx
# from datetime import datetime
# from main.logic.models import arbitrage_decision
# from main.config import settings
#
# def _fmt(n: float) -> str:
#     return f"{n:,.2f}"
#
# def build_message(decision: arbitrage_decision, pair: str) -> str:
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     return (
#         f"⏰ Time: {now}\n"
#         f"🔁 Pair: {pair}\n"
#         f"🟢 Buy @ {decision.buy_exchange}: {_fmt(decision.buy_price)} USDT\n"
#         f"🔴 Sell @ {decision.sell_exchange}: {_fmt(decision.sell_price)} USDT\n"
#         f"📈 Diff: {_fmt(decision.diff)}  ({decision.pct:.3f}%)\n\n"
#         f"Rule: threshold={settings.threshold_pct}% | min_vol={_fmt(settings.min_trade_usdt)} USDT"
#     )
#
# async def send_opportunity(decision: arbitrage_decision, pair: str) -> bool:
#     if not settings.bot_token or not settings.chat_id:
#         return False
#     text = build_message(decision, pair)
#     url = f"https://api.telegram.org/bot{settings.bot_token}/sendMessage"
#     async with httpx.AsyncClient(timeout=10) as client:
#         r = await client.post(url, json={"chat_id": settings.chat_id, "text": text, "parse_mode": "HTML"})
#         return r.status_code == 200

# test_telegram.py
# notifier_test.py
import os
import asyncio
import httpx

TOKEN = "your_token".strip()

API_BASE = f"https://api.telegram.org/bot{TOKEN}"

async def get_chat_id():
    url = f"{API_BASE}/getUpdates"  # دقت به حروف: U بزرگ
    print("GET:", url)
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url)
        print("HTTP:", r.status_code)
        try:
            data = r.json()
        except Exception:
            print("Body:", r.text)
            raise

        print("Body:", data)

        if not data.get("ok"):
            # اگر 404 بود، 99% متد یا URL اشتباه است
            raise RuntimeError(data)

        results = data.get("result", [])
        if not results:
            print("No updates yet. در تلگرام به ربات خودت /start بفرست و دوباره اجرا کن.")
            return None

        chat = results[-1].get("message", {}).get("chat", {})
        chat_id = chat.get("id")
        print("chat_id:", chat_id)
        return chat_id

async def send_test(chat_id: int):
    url = f"{API_BASE}/sendMessage"  # دقت به M بزرگ
    print("POST:", url)
    payload = {"chat_id": chat_id, "text": "Test ✅", "parse_mode": "HTML"}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(url, json=payload)
        print("HTTP:", r.status_code, r.text)
        return r.status_code == 200

async def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN خالی است.")
    chat_id = await get_chat_id()
    if chat_id:
        await send_test(chat_id)

if __name__ == "__main__":
    asyncio.run(main())

