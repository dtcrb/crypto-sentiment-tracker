import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Database:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    async def insert_or_update_coin(self, coingecko_id: str, symbol: str, name: str) -> int:
        # Check if coin exists
        existing = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: self.supabase.table("coins").select("id").eq("coingecko_id", coingecko_id).execute()
        )
        
        if existing.data:
            # Update existing coin
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.supabase.table("coins").update({
                    "symbol": symbol,
                    "name": name
                }).eq("coingecko_id", coingecko_id).execute()
            )
            return existing.data[0]['id']
        else:
            # Insert new coin
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.supabase.table("coins").insert({
                    "coingecko_id": coingecko_id,
                    "symbol": symbol,
                    "name": name
                }).execute()
            )
            return result.data[0]['id']
    
    async def insert_coin_price(self, coin_id: int, price_date: date, price_usd: float, market_cap: Optional[float]):
        # Check if price entry exists for this coin and date
        existing = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.supabase.table("coin_prices").select("id").eq("coin_id", coin_id).eq("date", price_date.isoformat()).execute()
        )
        
        price_data = {
            "coin_id": coin_id,
            "date": price_date.isoformat(),
            "price_usd": price_usd,
            "market_cap": market_cap
        }
        
        if existing.data:
            # Update existing price
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.supabase.table("coin_prices").update({
                    "price_usd": price_usd,
                    "market_cap": market_cap
                }).eq("coin_id", coin_id).eq("date", price_date.isoformat()).execute()
            )
        else:
            # Insert new price
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.supabase.table("coin_prices").insert(price_data).execute()
            )
    
    async def insert_article(self, title: str, summary: Optional[str], link: Optional[str], published_date: datetime) -> int:
        article_data = {
            "title": title,
            "summary": summary,
            "link": link,
            "published_date": published_date.isoformat()
        }
        
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.supabase.table("articles").insert(article_data).on_conflict("link").execute()
        )
        return result.data[0]['id']
    
    async def insert_coin_sentiment(self, coin_id: int, sentiment_date: date, sentiment_score: Optional[float], mentions_count: int, no_mentions: bool = False):
        # Check if sentiment entry exists for this coin and date
        existing = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.supabase.table("coin_sentiment").select("id").eq("coin_id", coin_id).eq("date", sentiment_date.isoformat()).execute()
        )
        
        sentiment_data = {
            "coin_id": coin_id,
            "date": sentiment_date.isoformat(),
            "sentiment_score": sentiment_score,
            "mentions_count": mentions_count,
            "no_mentions": no_mentions
        }
        
        if existing.data:
            # Update existing sentiment
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.supabase.table("coin_sentiment").update({
                    "sentiment_score": sentiment_score,
                    "mentions_count": mentions_count,
                    "no_mentions": no_mentions
                }).eq("coin_id", coin_id).eq("date", sentiment_date.isoformat()).execute()
            )
        else:
            # Insert new sentiment
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.supabase.table("coin_sentiment").insert(sentiment_data).execute()
            )
    
    async def get_all_coins(self) -> List[Dict[str, Any]]:
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.supabase.table("coins").select("id, coingecko_id, symbol, name").execute()
        )
        return result.data
    
    async def get_latest_coin_data(self) -> List[Dict[str, Any]]:
        # Use the view we created in the schema
        #result = await asyncio.get_event_loop().run_in_executor(
            #None,
            #lambda: self.supabase.table("latest_coin_data").select("*").not_("price_usd", "is", None).order("sentiment_score", desc=True).order("market_cap", desc=True).execute()
        #)
        query = self.supabase.table("latest_coin_data").select("*").order("sentiment_score", desc=True).order("market_cap", desc=True)
        result = query.execute()
        
        # Process the results to handle null sentiment scores properly
        processed_data = []
        for row in result.data:
            # Move null sentiment scores to the end
            if row.get('sentiment_score') is None or row.get('no_mentions'):
                row['_sort_score'] = -999
            else:
                row['_sort_score'] = row['sentiment_score']
            processed_data.append(row)
        
        # Sort by sentiment score (highest first), then by market cap
        processed_data.sort(key=lambda x: (x['_sort_score'], x.get('market_cap', 0) or 0), reverse=True)
        
        # Remove the temporary sort field
        for row in processed_data:
            if '_sort_score' in row:
                del row['_sort_score']
        
        return processed_data