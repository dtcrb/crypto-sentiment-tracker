from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from database import Database
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Crypto Sentiment Tracker API",
    description="API for tracking cryptocurrency sentiment based on news analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this more restrictively in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

@app.get("/")
async def root():
    return {"message": "Crypto Sentiment Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = await db.get_connection()
        await conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/api/coins", response_model=List[Dict[str, Any]])
async def get_coins():
    """
    Get the latest coin data including prices, market cap, and sentiment scores.
    Returns data sorted by sentiment score (highest first), then by market cap.
    """
    try:
        coins_data = await db.get_latest_coin_data()
        
        # Format the response
        formatted_coins = []
        for coin in coins_data:
            formatted_coin = {
                "coin_id": coin["coin_id"],
                "coingecko_id": coin["coingecko_id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price_usd": float(coin["price_usd"]) if coin["price_usd"] else None,
                "market_cap": float(coin["market_cap"]) if coin["market_cap"] else None,
                "sentiment_score": float(coin["sentiment_score"]) if coin["sentiment_score"] is not None else None,
                "mentions_count": coin["mentions_count"] if coin["mentions_count"] else 0,
                "no_mentions": coin["no_mentions"] if coin["no_mentions"] is not None else True
            }
            formatted_coins.append(formatted_coin)
        
        return formatted_coins
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coin data: {str(e)}")

@app.get("/api/coins/{coin_id}")
async def get_coin_details(coin_id: int):
    """Get detailed information for a specific coin"""
    try:
        conn = await db.get_connection()
        try:
            # Get coin basic info
            coin_result = await conn.fetchrow("""
                SELECT id, coingecko_id, symbol, name, created_at
                FROM coins WHERE id = $1
            """, coin_id)
            
            if not coin_result:
                raise HTTPException(status_code=404, detail="Coin not found")
            
            # Get recent prices (last 30 days)
            prices_result = await conn.fetch("""
                SELECT date, price_usd, market_cap
                FROM coin_prices 
                WHERE coin_id = $1 
                ORDER BY date DESC 
                LIMIT 30
            """, coin_id)
            
            # Get recent sentiment (last 30 days)
            sentiment_result = await conn.fetch("""
                SELECT date, sentiment_score, mentions_count, no_mentions
                FROM coin_sentiment 
                WHERE coin_id = $1 
                ORDER BY date DESC 
                LIMIT 30
            """, coin_id)
            
            return {
                "coin": dict(coin_result),
                "recent_prices": [dict(row) for row in prices_result],
                "recent_sentiment": [dict(row) for row in sentiment_result]
            }
            
        finally:
            await conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching coin details: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)