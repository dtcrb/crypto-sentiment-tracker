from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any, Tuple
import re
from datetime import date

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        
    def analyze_text(self, text: str) -> float:
        """Analyze sentiment of text using VADER and return compound score"""
        if not text:
            return 0.0
        
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']
    
    def find_coin_mentions(self, text: str, coins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find which coins are mentioned in the text"""
        mentioned_coins = []
        text_lower = text.lower()
        
        for coin in coins:
            coin_name = coin['name'].lower()
            coin_symbol = coin['symbol'].lower()
            
            # Create regex patterns for exact matches
            name_pattern = r'\b' + re.escape(coin_name) + r'\b'
            symbol_pattern = r'\b' + re.escape(coin_symbol) + r'\b'
            
            name_matches = len(re.findall(name_pattern, text_lower))
            symbol_matches = len(re.findall(symbol_pattern, text_lower))
            
            total_mentions = name_matches + symbol_matches
            
            if total_mentions > 0:
                mentioned_coins.append({
                    'coin_id': coin['id'],
                    'coingecko_id': coin['coingecko_id'],
                    'symbol': coin['symbol'],
                    'name': coin['name'],
                    'mentions': total_mentions
                })
        
        return mentioned_coins
    
    def analyze_articles_for_coins(self, articles: List[Dict[str, Any]], coins: List[Dict[str, Any]], analysis_date: date) -> Dict[int, Dict[str, Any]]:
        """Analyze all articles and aggregate sentiment by coin"""
        coin_sentiment_data = {}
        
        # Initialize all coins with zero mentions
        for coin in coins:
            coin_sentiment_data[coin['id']] = {
                'coin_id': coin['id'],
                'total_mentions': 0,
                'sentiment_scores': [],
                'sentiment_score': None,
                'no_mentions': True
            }
        
        # Process each article
        for article in articles:
            # Combine title and summary for analysis
            full_text = f"{article.get('title', '')} {article.get('summary', '')}"
            
            # Find mentioned coins
            mentioned_coins = self.find_coin_mentions(full_text, coins)
            
            if mentioned_coins:
                # Analyze sentiment of the article
                sentiment_score = self.analyze_text(full_text)
                
                # Add sentiment to each mentioned coin
                for mentioned_coin in mentioned_coins:
                    coin_id = mentioned_coin['coin_id']
                    mentions = mentioned_coin['mentions']
                    
                    coin_sentiment_data[coin_id]['total_mentions'] += mentions
                    coin_sentiment_data[coin_id]['no_mentions'] = False
                    
                    # Add sentiment score weighted by number of mentions
                    for _ in range(mentions):
                        coin_sentiment_data[coin_id]['sentiment_scores'].append(sentiment_score)
        
        # Calculate average sentiment for each coin
        for coin_id, data in coin_sentiment_data.items():
            if data['sentiment_scores']:
                data['sentiment_score'] = sum(data['sentiment_scores']) / len(data['sentiment_scores'])
            else:
                data['sentiment_score'] = None
        
        return coin_sentiment_data