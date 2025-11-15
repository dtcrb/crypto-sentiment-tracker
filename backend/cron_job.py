import asyncio
import os
import sys
from datetime import date, datetime
from database import Database
from coingecko_client import CoinGeckoClient
from rss_parser import RSSParser
from sentiment_analyzer import SentimentAnalyzer


def fetch_top_coins(coingecko: CoinGeckoClient, limit: int = 100):
    print("Fetching top 100 coins from CoinGecko...")
    coins_data = coingecko.get_top_coins(limit=limit)
    if not coins_data:
        print("Failed to fetch coin data from CoinGecko")
        return []
    print(f"Fetched {len(coins_data)} coins")
    return coins_data


async def upsert_coins_and_prices(db: Database, coins_data, today: date):
    print("Updating coin data in database...")
    coin_ids_map = {}
    for coin_data in coins_data:
        try:
            coin_id = await db.insert_or_update_coin(
                coingecko_id=coin_data["coingecko_id"],
                symbol=coin_data["symbol"],
                name=coin_data["name"],
            )

            await db.insert_coin_price(
                coin_id=coin_id,
                price_date=today,
                price_usd=coin_data["price_usd"],
                market_cap=coin_data["market_cap"],
            )

            coin_ids_map[coin_data["coingecko_id"]] = {
                "id": coin_id,
                "coingecko_id": coin_data["coingecko_id"],
                "symbol": coin_data["symbol"],
                "name": coin_data["name"],
            }

        except Exception as e:
            print(f"Error processing coin {coin_data.get('coingecko_id', 'unknown')}: {e}")
            continue

    print(f"Updated {len(coin_ids_map)} coins in database")
    return coin_ids_map


def fetch_rss_articles(rss_parser: RSSParser, max_feeds: int = None):
    print("Fetching RSS feeds...")
    articles = rss_parser.parse_all_feeds(max_feeds)
    if not articles:
        print("No articles found from RSS feeds")
        return []
    return articles


async def store_articles(db: Database, articles):
    print(f"Storing {len(articles)} articles in database...")
    for article in articles:
        try:
            await db.insert_article(
                title=article["title"],
                summary=article["summary"],
                link=article["link"],
                published_date=article["published_date"],
            )
        except Exception as e:
            print(f"Error storing article: {e}")
            continue


def analyze_sentiment(sentiment_analyzer: SentimentAnalyzer, articles, coins_list, today: date):
    print("Analyzing sentiment...")
    return sentiment_analyzer.analyze_articles_for_coins(articles, coins_list, today)


async def store_sentiment_data(db: Database, sentiment_data, today: date):
    print("Storing sentiment data...")
    for coin_id, sentiment_info in sentiment_data.items():
        try:
            await db.insert_coin_sentiment(
                coin_id=coin_id,
                sentiment_date=today,
                sentiment_score=sentiment_info["sentiment_score"],
                mentions_count=sentiment_info["total_mentions"],
                no_mentions=sentiment_info["no_mentions"],
            )
        except Exception as e:
            print(f"Error storing sentiment for coin {coin_id}: {e}")
            continue


def print_summary(articles, sentiment_data, coins_data):
    total_mentions = sum(data["total_mentions"] for data in sentiment_data.values())
    coins_with_mentions = sum(1 for data in sentiment_data.values() if not data["no_mentions"])

    print("Summary:")
    print(f"- Processed {len(articles)} articles")
    print(f"- Found {total_mentions} total coin mentions")
    print(f"- {coins_with_mentions} coins were mentioned")
    print(f"- Updated data for {len(coins_data)} coins")


async def run_daily_update(max_feeds: int = None):
    """Main function that runs the daily data collection and analysis"""
    print(f"Starting daily update at {datetime.now()}")

    try:
        # Initialize components
        db = Database()
        coingecko = CoinGeckoClient(api_key=os.getenv("COINGECKO_API_KEY"))
        rss_parser = RSSParser()
        sentiment_analyzer = SentimentAnalyzer()

        today = date.today()

        # Step 1: Fetch top coins
        coins_data = fetch_top_coins(coingecko, limit=100)
        if not coins_data:
            return

        articles = fetch_rss_articles(rss_parser, max_feeds)
        if not articles:
            return

        coin_ids_map = await upsert_coins_and_prices(db, coins_data, today)
        
        await store_articles(db, articles)

        coins_list = list(coin_ids_map.values())
        sentiment_data = analyze_sentiment(sentiment_analyzer, articles, coins_list, today)

        await store_sentiment_data(db, sentiment_data, today)

        print(f"Daily update completed successfully at {datetime.now()}")

        # Print summary
        print_summary(articles, sentiment_data, coins_data)

    except Exception as e:
        print(f"Error during daily update: {e}")
        raise

if __name__ == "__main__":
    # if run with --test, process only 1 feed
    if "--test" in sys.argv:
        asyncio.run(run_daily_update(3))
    else:
        asyncio.run(run_daily_update(None))