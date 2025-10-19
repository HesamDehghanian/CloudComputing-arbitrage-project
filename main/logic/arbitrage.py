from main.logic.models import prices_data, arbitrage_decision


def calculate(buy_price: float, sell_price: float) -> tuple[float, float]:
    difference = sell_price - buy_price
    if buy_price:
        benefit_percent = (difference / buy_price) * 100
    else:
        benefit_percent = 0.0

    return difference, benefit_percent


def decide(from_nobitex: prices_data, from_wallex: prices_data, threshold: float,
           min_trade_usdt: float) -> arbitrage_decision:
    if not from_nobitex.ok or not from_wallex.ok:
        return arbitrage_decision(
            buy_exchange=from_nobitex.exchange_name,
            sell_exchange=from_wallex.exchange_name,
            buy_price=from_nobitex.last_price,
            sell_price=from_wallex.last_price,
            diff=0.0,
            pct=0.0,
            is_opportunity=False
        )

    difference1, benefit_percent1 = calculate(from_nobitex.last_price,
                                              from_wallex.last_price)  # Buy Nobitex → Sell Wallex
    difference2, benefit_percent2 = calculate(from_wallex.last_price,
                                              from_nobitex.last_price)  # Buy Wallex → Sell Nobitex

    if difference1 >= difference2:
        buy_ex, sell_ex = from_nobitex, from_wallex
        difference, benefit_percent = difference1, benefit_percent1
    else:
        buy_ex, sell_ex = from_wallex, from_nobitex
        difference, benefit_percent = difference2, benefit_percent2

    if benefit_percent >= threshold and min_trade_usdt > 0:
        is_opp = True

    return arbitrage_decision(
        buy_exchange=buy_ex.exchange_name,
        sell_exchange=sell_ex.exchange_name,
        buy_price=buy_ex.last_price,
        sell_price=sell_ex.last_price,
        diff=difference,
        pct=benefit_percent,
        is_opportunity=is_opp
    )
