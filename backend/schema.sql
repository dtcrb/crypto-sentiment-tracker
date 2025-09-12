-- Crypto Sentiment Tracker Database Schema

-- Create coins table
CREATE TABLE coins (
    id SERIAL PRIMARY KEY,
    coingecko_id TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create coin_prices table
CREATE TABLE coin_prices (
    id SERIAL PRIMARY KEY,
    coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    price_usd NUMERIC(20, 8) NOT NULL,
    market_cap NUMERIC(20, 2),
    UNIQUE(coin_id, date)
);

-- Create articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    link TEXT,
    published_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create coin_sentiment table
CREATE TABLE coin_sentiment (
    id SERIAL PRIMARY KEY,
    coin_id INTEGER REFERENCES coins(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sentiment_score FLOAT,
    mentions_count INTEGER DEFAULT 0,
    no_mentions BOOLEAN DEFAULT FALSE,
    UNIQUE(coin_id, date)
);

-- Create indexes for better performance
CREATE INDEX idx_coins_coingecko_id ON coins(coingecko_id);
CREATE INDEX idx_coin_prices_coin_id_date ON coin_prices(coin_id, date);
CREATE INDEX idx_coin_sentiment_coin_id_date ON coin_sentiment(coin_id, date);
CREATE INDEX idx_articles_published_date ON articles(published_date);

-- Create a view for the latest coin data (useful for the API)
CREATE VIEW latest_coin_data AS
SELECT 
    c.id as coin_id,
    c.coingecko_id,
    c.symbol,
    c.name,
    cp.price_usd,
    cp.market_cap,
    cs.sentiment_score,
    cs.mentions_count,
    cs.no_mentions,
    cp.date as price_date,
    cs.date as sentiment_date
FROM coins c
LEFT JOIN coin_prices cp ON c.id = cp.coin_id 
    AND cp.date = (SELECT MAX(date) FROM coin_prices WHERE coin_id = c.id)
LEFT JOIN coin_sentiment cs ON c.id = cs.coin_id 
    AND cs.date = (SELECT MAX(date) FROM coin_sentiment WHERE coin_id = c.id)
ORDER BY cp.market_cap DESC NULLS LAST;