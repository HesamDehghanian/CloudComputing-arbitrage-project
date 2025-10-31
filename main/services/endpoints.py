from fastapi import FastAPI
from main.flow.metrics import metrics_response
from main.connection.nobitex import fetch_price_btcusdt as nobitex_price
from main.connection.wallex import fetch_price_btcusdt as wallex_price
from main.logic.arbitrage import decide
from main.config import settings
import asyncio
from main.services.scheduler import run_loop

def create_app() -> FastAPI:
    app = FastAPI(title="Arbitrage Service", version="1.0.0")

    @app.on_event("startup")
    async def _start_background_loop():
        asyncio.create_task(run_loop())

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.get("/prices")
    async def prices(pair: str = "BTCUSDT"):
        nob = await nobitex_price()
        wal = await wallex_price()
        return {"pair": pair, "nobitex": nob, "wallex": wal}

    @app.get("/arbitrage")
    async def arbitrage(pair: str = "BTCUSDT"):
        nob = await nobitex_price()
        wal = await wallex_price()
        decision = decide(nob, wal, settings.threshold_pct, settings.min_trade_usdt)
        return {"pair": pair, "decision": decision}

    @app.get("/metrics")
    async def metrics():
        return metrics_response()

    from main.db import db_ping

    @app.get("/db/health")
    async def db_health():
        await db_ping()
        return {"db_ok": True}


    return app
