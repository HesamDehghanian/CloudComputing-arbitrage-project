from typing import Optional
from pydantic import BaseModel

class prices_data(BaseModel):
    exchange_name: str
    our_symbol: str
    exchange_symbol: str
    last_price: float
    last_update_time: Optional[int] = None
    ok: bool = True
    error: Optional[str] = None

class arbitrage_decision(BaseModel):
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    diff: float
    pct: float
    is_opportunity: bool
