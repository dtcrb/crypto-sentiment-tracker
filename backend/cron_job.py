import asyncio
import os
from datetime import date, datetime
from database import Database
from coingecko_client import CoinGeckoClient
from rss_parser import RSSParser
from sentiment_analyzer import SentimentAnalyzer

async def run_daily_update():
    """Main function that runs the daily data collection and analysis"""
    print(f"Starting daily update at {datetime.now()}")
    
    try:
        # Initialize components
        db = Database()
        coingecko = CoinGeckoClient(api_key=os.getenv("COINGECKO_API_KEY"))
        rss_parser = RSSParser()
        sentiment_analyzer = SentimentAnalyzer()
        
        today = date.today()
        
        # Step 1: Fetch top 100 coins from CoinGecko
        print("Fetching top 100 coins from CoinGecko...")
        coins_data = coingecko.get_top_coins(limit=100)
        
        if not coins_data:
            print("Failed to fetch coin data from CoinGecko")
            return
        
        print(f"Fetched {len(coins_data)} coins")
        
        # Step 2: Insert/update coins and their prices
        print("Updating coin data in database...")
        coin_ids_map = {}
        
        for coin_data in coins_data:
            try:
                coin_id = await db.insert_or_update_coin(
                    coingecko_id=coin_data['coingecko_id'],
                    symbol=coin_data['symbol'],
                    name=coin_data['name']
                )
                
                await db.insert_coin_price(
                    coin_id=coin_id,
                    price_date=today,
                    price_usd=coin_data['price_usd'],
                    market_cap=coin_data['market_cap']
                )
                
                coin_ids_map[coin_data['coingecko_id']] = {
                    'id': coin_id,
                    'coingecko_id': coin_data['coingecko_id'],
                    'symbol': coin_data['symbol'],
                    'name': coin_data['name']
                }
                
            except Exception as e:
                print(f"Error processing coin {coin_data['coingecko_id']}: {e}")
                continue
        
        print(f"Updated {len(coin_ids_map)} coins in database")
        
        # Step 3: Fetch and parse RSS feeds
        print("Fetching RSS feeds...")
        articles = rss_parser.parse_all_feeds()
        
        if not articles:
            print("No articles found from RSS feeds")
            return
        
        # Step 4: Store articles in database
       # print(f"Storing {len(articles)} articles in database...")
       # for article in articles:
       #     try:
       #         await db.insert_article(
       #             title=article['title'],
       #             summary=article['summary'],
       #             link=article['link'],
       #             published_date=article['published_date']
       #         )
       #     except Exception as e:
       #         print(f"Error storing article: {e}")
       #         continue
       # 
        # Step 5: Analyze sentiment
        print("Analyzing sentiment...")
        coins_list = list(coin_ids_map.values())
        sentiment_data = sentiment_analyzer.analyze_articles_for_coins(articles, coins_list, today)
        
        # Step 6: Store sentiment data
        print("Storing sentiment data...")
        for coin_id, sentiment_info in sentiment_data.items():
            try:
                await db.insert_coin_sentiment(
                    coin_id=coin_id,
                    sentiment_date=today,
                    sentiment_score=sentiment_info['sentiment_score'],
                    mentions_count=sentiment_info['total_mentions'],
                    no_mentions=sentiment_info['no_mentions']
                )
            except Exception as e:
                print(f"Error storing sentiment for coin {coin_id}: {e}")
                continue
        
        print(f"Daily update completed successfully at {datetime.now()}")
        
        # Print summary
        total_mentions = sum(data['total_mentions'] for data in sentiment_data.values())
        coins_with_mentions = sum(1 for data in sentiment_data.values() if not data['no_mentions'])
        
        print(f"Summary:")
        print(f"- Processed {len(articles)} articles")
        print(f"- Found {total_mentions} total coin mentions")
        print(f"- {coins_with_mentions} coins were mentioned")
        print(f"- Updated data for {len(coins_data)} coins")
        
    except Exception as e:
        print(f"Error during daily update: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(run_daily_update())