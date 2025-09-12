# Crypto Sentiment Tracker Backend

FastAPI backend service for the crypto sentiment tracker that collects cryptocurrency data, analyzes news sentiment, and provides API endpoints.

## Setup

1. **Install Dependencies** (use a venv)
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials
   ```

3. **Database Setup**
   - Ensure PostgreSQL database is running (Supabase)
   - Run the schema.sql file to create tables

## Running the Application

### Development Server
```bash
python main.py
```
The API will be available at `http://localhost:8000`

### Daily Cron Job
```bash
python cron_job.py
```

## API Endpoints

### GET /api/coins
Returns the latest coin data with sentiment analysis:
```json
[
  {
    "coin_id": 1,
    "coingecko_id": "bitcoin",
    "symbol": "BTC",
    "name": "Bitcoin",
    "price_usd": 45000.50,
    "market_cap": 850000000000,
    "sentiment_score": 0.25,
    "mentions_count": 15,
    "no_mentions": false
  }
]
```

### GET /api/coins/{coin_id}
Returns detailed information for a specific coin including 30-day history.

### GET /health
Health check endpoint for monitoring.

## Cron Job Details

The `cron_job.py` script should be run daily and performs:

1. **Fetch Top 100 Coins** from CoinGecko API
2. **Parse RSS Feeds** from major crypto news sources
3. **Analyze Sentiment** using VADER sentiment analysis
4. **Store Results** in PostgreSQL database

### RSS Feed Sources
- CoinDesk
- Cointelegraph  
- Decrypt
- NewsBTC
- Bitcoin Magazine

### Sentiment Analysis
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner) to analyze:
- Article titles and summaries
- Coin mentions (name and symbol matching)
- Compound sentiment scores (-1 to 1)

## Deployment

### Scheduling the Cron Job

**Option 1: System Cron (Linux/Mac)**
```bash
# Add to crontab (run daily at 6 AM)
0 6 * * * cd /path/to/backend && python cron_job.py
```

**Option 2: GitHub Actions**
```yaml
# .github/workflows/daily-update.yml
name: Daily Crypto Update
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run daily update
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          cd backend
          python cron_job.py
```

**Option 3: Cloud Functions**
Deploy as a cloud function (AWS Lambda, Google Cloud Functions, etc.) with scheduled triggers.

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `COINGECKO_API_KEY`: (Optional) CoinGecko API key for higher rate limits

## Rate Limiting

The application includes built-in rate limiting for external APIs:
- CoinGecko: 1.2 second delays between requests
- RSS feeds: 1 second delays between feeds

## Error Handling

- Comprehensive error logging
- Graceful handling of API failures
- Database transaction safety
- Duplicate data prevention with UPSERT operations

## Python version
3.12.6
