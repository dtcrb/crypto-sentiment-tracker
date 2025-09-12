# Database Setup

## PostgreSQL Schema for Crypto Sentiment Tracker

This directory contains the database schema for the crypto sentiment tracker application.

## Setup Instructions

1. Connect to your Supabase PostgreSQL database:
   ```
   https://eorprovjzivlbgpjnraz.supabase.co
   ```

2. Run the schema.sql file to create all tables and indexes:
   ```sql
   -- Execute the contents of schema.sql in your Supabase SQL editor
   ```

## Tables

### coins
- Stores basic information about cryptocurrencies
- Primary key: `id`
- Unique constraint on `coingecko_id`

### coin_prices
- Daily price and market cap data for each coin
- Foreign key to `coins.id`
- Unique constraint on `(coin_id, date)` to prevent duplicates

### articles
- RSS feed articles from crypto news sources
- Stores title, summary, link, and publication date

### coin_sentiment
- Daily sentiment analysis results for each coin
- Foreign key to `coins.id`
- `sentiment_score`: VADER compound score (-1 to 1)
- `mentions_count`: Number of times coin was mentioned
- `no_mentions`: Boolean flag for coins not mentioned that day

## Views

### latest_coin_data
- Convenient view that joins the latest price and sentiment data for each coin
- Used by the API endpoint to efficiently retrieve current data