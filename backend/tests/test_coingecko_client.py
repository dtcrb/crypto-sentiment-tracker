import requests
from backend.coingecko_client import CoinGeckoClient


def test_get_top_coins_success_and_params(monkeypatch):
    client = CoinGeckoClient()

    captured = {}

    def fake_get(url, params=None):
        captured["url"] = url
        captured["params"] = params or {}

        class Resp:
            def raise_for_status(self):
                return None

            def json(self):
                return [
                    {
                        "id": "bitcoin",
                        "symbol": "btc",
                        "name": "Bitcoin",
                        "current_price": 12345.67,
                        "market_cap": 100.5,
                        "last_updated": "2024-01-01T12:34:56Z",
                    },
                    {
                        "id": "nullcoin",
                        "symbol": "nul",
                        "name": "NullCoin",
                        "current_price": None,
                        "market_cap": None,
                        "last_updated": "2024-01-02T00:00:00Z",
                    },
                ]

        return Resp()

    monkeypatch.setattr(client.session, "get", fake_get)

    coins = client.get_top_coins(limit=5)

    assert captured["url"].endswith("/coins/markets")
    assert captured["params"]["per_page"] == 5

    assert coins[0]["coingecko_id"] == "bitcoin"
    assert coins[0]["symbol"] == "BTC"
    assert coins[0]["name"] == "Bitcoin"
    assert coins[0]["price_usd"] == 12345.67
    assert coins[0]["market_cap"] == 100.5
    assert coins[0]["last_updated"].isoformat() == "2024-01-01T12:34:56+00:00"

    # Fallbacks for None values
    assert coins[1]["price_usd"] == 0.0
    assert coins[1]["market_cap"] == 0.0


def test_get_top_coins_http_error(monkeypatch):
    client = CoinGeckoClient()

    class Resp:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("Bad Request")

    def fake_get(url, params=None):
        return Resp()

    monkeypatch.setattr(client.session, "get", fake_get)

    coins = client.get_top_coins()
    assert coins == []


def test_get_top_coins_unexpected_exception(monkeypatch):
    client = CoinGeckoClient()

    class Resp:
        def raise_for_status(self):
            return None

        def json(self):
            raise ValueError("boom")

    def fake_get(url, params=None):
        return Resp()

    monkeypatch.setattr(client.session, "get", fake_get)

    coins = client.get_top_coins()
    assert coins == []


def test_api_key_header_set():
    c1 = CoinGeckoClient(api_key=None)
    assert "X-CG-API-Key" not in c1.session.headers

    c2 = CoinGeckoClient(api_key="abc123")
    assert c2.session.headers.get("X-CG-API-Key") == "abc123"


def test_rate_limit_delay(monkeypatch):
    client = CoinGeckoClient()
    called = {}

    def fake_sleep(seconds):
        called["seconds"] = seconds

    monkeypatch.setattr("backend.coingecko_client.time.sleep", fake_sleep)

    client.rate_limit_delay()

    assert called["seconds"] == 1.2




