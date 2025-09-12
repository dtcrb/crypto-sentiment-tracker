import requests
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import time

class CoinGeckoClient:
    def __init__(self, api_key: str = None):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = api_key
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({"X-CG-API-Key": self.api_key})
    
    def get_top_coins(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch top coins by market cap from CoinGecko"""
        url = f"{self.base_url}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            coins = response.json()
            
            processed_coins = []
            for coin in coins:
                processed_coin = {
                    "coingecko_id": coin["id"],
                    "symbol": coin["symbol"].upper(),
                    "name": coin["name"],
                    "price_usd": float(coin["current_price"]) if coin["current_price"] else 0.0,
                    "market_cap": float(coin["market_cap"]) if coin["market_cap"] else 0.0,
                    "last_updated": datetime.fromisoformat(coin["last_updated"].replace("Z", "+00:00"))
                }
                processed_coins.append(processed_coin)
            
            return processed_coins
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coins from CoinGecko: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def rate_limit_delay(self):
        """Add delay to respect rate limits (CoinGecko free tier: ~10-50 calls/minute)"""
        time.sleep(1.2)  # Conservative delay