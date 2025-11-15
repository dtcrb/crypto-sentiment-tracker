import asyncio
from datetime import date, datetime, timezone
import pytest

from backend.database import Database


@pytest.mark.asyncio
async def test_insert_or_update_coin_inserts_when_missing(fake_supabase):
    db = Database()

    coin_id = await db.insert_or_update_coin("bitcoin", "btc", "Bitcoin")

    coins = fake_supabase["coins"]
    assert len(coins) == 1
    assert coins[0]["coingecko_id"] == "bitcoin"
    assert coins[0]["symbol"] == "btc"
    assert coins[0]["name"] == "Bitcoin"
    assert coin_id == coins[0]["id"]


@pytest.mark.asyncio
async def test_insert_or_update_coin_updates_when_exists(fake_supabase):
    db = Database()
    # seed existing coin
    fake_supabase.setdefault("coins", []).append({
        "id": 1,
        "coingecko_id": "bitcoin",
        "symbol": "old",
        "name": "Old"
    })

    coin_id = await db.insert_or_update_coin("bitcoin", "btc", "Bitcoin")

    coins = fake_supabase["coins"]
    assert len(coins) == 1
    assert coin_id == 1
    assert coins[0]["symbol"] == "btc"
    assert coins[0]["name"] == "Bitcoin"


@pytest.mark.asyncio
async def test_insert_coin_price_insert_and_update_paths(fake_supabase):
    db = Database()
    # seed a coin id 1
    fake_supabase.setdefault("coins", []).append({"id": 1, "coingecko_id": "bitcoin", "symbol": "btc", "name": "Bitcoin"})

    d = date(2024, 1, 1)
    await db.insert_coin_price(1, d, 42000.0, 800_000_000_000.0)

    prices = fake_supabase["coin_prices"]
    assert len(prices) == 1
    assert prices[0]["coin_id"] == 1
    assert prices[0]["date"] == d.isoformat()
    assert prices[0]["price_usd"] == 42000.0

    # update branch
    await db.insert_coin_price(1, d, 43000.0, 810_000_000_000.0)
    assert len(prices) == 1
    assert prices[0]["price_usd"] == 43000.0


@pytest.mark.asyncio
async def test_insert_article_respects_on_conflict_link(fake_supabase):
    db = Database()

    published = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    first_id = await db.insert_article("Title", "Summary", "http://example.com/a", published)
    second_id = await db.insert_article("Title 2", "Summary 2", "http://example.com/a", published)

    articles = fake_supabase["articles"]
    # only one row due to on_conflict(link)
    assert len(articles) == 1
    assert first_id == second_id == articles[0]["id"]


@pytest.mark.asyncio
async def test_insert_coin_sentiment_insert_then_update(fake_supabase):
    db = Database()

    d = date(2024, 2, 1)
    await db.insert_coin_sentiment(1, d, 0.5, 10, False)

    sentiments = fake_supabase["coin_sentiment"]
    assert len(sentiments) == 1
    assert sentiments[0]["sentiment_score"] == 0.5
    assert sentiments[0]["mentions_count"] == 10

    # update branch
    await db.insert_coin_sentiment(1, d, 0.1, 2, True)
    assert len(sentiments) == 1
    assert sentiments[0]["sentiment_score"] == 0.1
    assert sentiments[0]["mentions_count"] == 2
    assert sentiments[0]["no_mentions"] is True


@pytest.mark.asyncio
async def test_get_all_coins_returns_rows(fake_supabase):
    db = Database()

    fake_supabase.setdefault("coins", []).extend([
        {"id": 1, "coingecko_id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
        {"id": 2, "coingecko_id": "ethereum", "symbol": "eth", "name": "Ethereum"},
    ])

    rows = await db.get_all_coins()
    assert [r["id"] for r in rows] == [1, 2]


@pytest.mark.asyncio
async def test_get_latest_coin_data_sorts_nulls_last_and_by_market_cap(fake_supabase):
    db = Database()

    fake_supabase.setdefault("latest_coin_data", []).extend([
        {"id": 1, "coingecko_id": "b", "sentiment_score": None, "no_mentions": False, "market_cap": 100},
        {"id": 2, "coingecko_id": "a", "sentiment_score": 0.8, "no_mentions": False, "market_cap": 50},
        {"id": 3, "coingecko_id": "c", "sentiment_score": 0.8, "no_mentions": False, "market_cap": 200},
        {"id": 4, "coingecko_id": "d", "sentiment_score": 0.2, "no_mentions": True, "market_cap": 999},
    ])

    rows = await db.get_latest_coin_data()
    # Expect id 3 (0.8, cap 200) before id 2 (0.8, cap 50), then 4&1 last due to null/no_mentions
    assert [r["id"] for r in rows] == [3, 2, 4, 1]


@pytest.mark.asyncio
async def test_get_recent_articles_for_coin_filters_by_name_and_symbol_and_limits(fake_supabase):
    db = Database()

    # Seed coin
    fake_supabase.setdefault("coins", []).append({
        "id": 1,
        "coingecko_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
    })

    # Seed articles
    fake_supabase.setdefault("articles", []).extend([
        {"id": 1, "title": "Markets rally", "summary": "Stocks up", "link": "u1", "published_date": "2024-01-02T00:00:00Z"},
        {"id": 2, "title": "Bitcoin hits new ATH", "summary": "BTC surges", "link": "u2", "published_date": "2024-01-03T00:00:00Z"},
        {"id": 3, "title": "ETH upgrade", "summary": "Ethereum news", "link": "u3", "published_date": "2024-01-04T00:00:00Z"},
        {"id": 4, "title": "Crypto digest", "summary": "Bitcoin falls", "link": "u4", "published_date": "2024-01-05T00:00:00Z"},
        {"id": 5, "title": "BTC whales move", "summary": "On-chain data", "link": "u5", "published_date": "2024-01-06T00:00:00Z"},
    ])

    # Limit 2 should return the two most recent that mention Bitcoin/BTC
    results = await db.get_recent_articles_for_coin(coin_id=1, limit=2)
    assert [r["id"] for r in results] == [5, 4]

    # No coin -> empty
    empty = await db.get_recent_articles_for_coin(coin_id=999, limit=10)
    assert empty == []
