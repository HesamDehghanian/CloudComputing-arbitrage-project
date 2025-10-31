from sqlalchemy import text
from main.db import SessionLocal

async def _get_id(conn, table, name_col, name_val):
    row = await conn.execute(text(f"SELECT id FROM {table} WHERE {name_col}=:v LIMIT 1"), {"v": name_val})
    r = row.first()
    if r: return r[0]
    row = await conn.execute(text(f"INSERT INTO {table}({name_col}) VALUES(:v) ON CONFLICT DO NOTHING RETURNING id"), {"v": name_val})
    r = row.first()
    if r: return r[0]
    row = await conn.execute(text(f"SELECT id FROM {table} WHERE {name_col}=:v LIMIT 1"), {"v": name_val})
    return row.first()[0]

async def save_tick(exchange_name: str, pair_symbol: str, price: float):
    async with SessionLocal() as s:
        async with s.begin():
            ex_id = await _get_id(s, "exchanges", "name", exchange_name)
            pr_id = await _get_id(s, "pairs", "symbol", pair_symbol)
            await s.execute(
                text("INSERT INTO ticks(exchange_id, pair_id, price) VALUES(:e,:p,:pr)"),
                {"e": ex_id, "p": pr_id, "pr": price}
            )

async def save_opportunity(pair_symbol: str, buy_ex: str, sell_ex: str,
                           diff_abs: float, diff_pct: float, est_profit_usd: float | None = None) -> int:
    async with SessionLocal() as s:
        async with s.begin():
            pr_id = await _get_id(s, "pairs", "symbol", pair_symbol)
            buy_id = await _get_id(s, "exchanges", "name", buy_ex)
            sell_id = await _get_id(s, "exchanges", "name", sell_ex)
            res = await s.execute(
                text("""INSERT INTO opportunities(pair_id,buy_exchange_id,sell_exchange_id,diff_abs,diff_pct,est_profit_usd)
                        VALUES(:p,:b,:s,:da,:dp,:ep) RETURNING id"""),
                {"p": pr_id, "b": buy_id, "s": sell_id, "da": diff_abs, "dp": diff_pct, "ep": est_profit_usd}
            )
            return res.scalar_one()
