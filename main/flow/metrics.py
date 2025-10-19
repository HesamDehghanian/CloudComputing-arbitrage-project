from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import PlainTextResponse

ok_requests_number = Counter("requests_ok_total", "Successful requests", ["exchange"])
error_requests_number = Counter("requests_err_total", "Failed requests", ["exchange"])
found_arbitrage_number = Counter("arbitrage_found_total", "Arbitrage opportunities found", ["pair"])
exchange_latency = Histogram("exchange_latency_seconds", "Latency per exchange", ["exchange"])

last_different_prices = Gauge("last_different_prices", "Last observed spread per pair", ["pair"])
last_benefit_percent = Gauge("last_benefit_percent", "Last observed spread percent per pair", ["pair"])


def calculate_latency(exchange: str, seconds: float) -> None:
    exchange_latency.labels(exchange=exchange).observe(seconds)


def set_request_ok(exchange: str) -> None:
    ok_requests_number.labels(exchange=exchange).inc()


def set_request_error(exchange: str) -> None:
    error_requests_number.labels(exchange=exchange).inc()


def set_spread(pair: str, difference: float, benefit_percent: float) -> None:
    last_different_prices.labels(pair=pair).set(difference)
    last_benefit_percent.labels(pair=pair).set(benefit_percent)


def opportunity_found(pair: str) -> None:
    found_arbitrage_number.labels(pair=pair).inc()


def metrics_response():
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
