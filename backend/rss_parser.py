import feedparser
import requests
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import time

class RSSParser:
    def __init__(self):
        self.feeds = [
            "https://www.coindesk.com/arc/outboundfeeds/rss/"
            "https://cointelegraph.com/rss",
            "https://decrypt.co/feed",
            "https://www.newsbtc.com/feed/",
            "https://bitcoinmagazine.com/.rss/full/",
            "https://cryptoslate.com/feed/",
            "https://www.cryptonews.com/news/feed/",
            "https://blockchain.news/feed",
            "https://www.ccn.com/news/crypto-news/feeds/",
            "https://www.ccn.com/analysis/crypto-analysis/feeds/",
            "https://coinjournal.net/feeds/",
            "https://thedefiant.io/feed/",
            "https://cryptopotato.com/feed/",
            "https://livebitcoinnews.com/feed/",
            "https://cryptoninjas.net/feed/",
            "https://ambcrypto.com/feed/",
            "https://u.today/rss",
            "https://www.investing.com/rss/news_25.rss",
            "https://bitcoinist.com/feed/",
            "https://cryptobriefing.com/feed/",
            "https://beincrypto.com/feed/",
            "https://cryptonewsflash.com/feed/",
            "https://finbold.com/feed/",
            "https://blockonomi.com/feed/",
        ]
        
    def parse_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Parse a single RSS feed and return articles"""
        try:
            print(f"Parsing feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"Warning: Feed may be malformed: {feed_url}")
            
            articles = []
            for entry in feed.entries:
                try:
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                    else:
                        published_date = datetime.now(datetime.timezone.utc)
                    
                    # last 7 days
                    if published_date < datetime.now(timezone.utc) - timedelta(days=7):
                        continue

                    article = {
                        "title": getattr(entry, 'title', ''),
                        "summary": getattr(entry, 'summary', '') or getattr(entry, 'description', ''),
                        "link": getattr(entry, 'link', ''),
                        "published_date": published_date
                    }
                    
                    if article["title"]:
                        articles.append(article)
                        
                except Exception as e:
                    print(f"Error parsing entry from {feed_url}: {e}")
                    continue
            
            print(f"Parsed {len(articles)} articles from {feed_url}")
            return articles
            
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error parsing feed {feed_url}: {e}")
            return []
    
    def parse_all_feeds(self) -> List[Dict[str, Any]]:
        """Parse all RSS feeds and return combined articles"""
        all_articles = []
        
        for feed_url in self.feeds:
            articles = self.parse_feed(feed_url)
            all_articles.extend(articles)
            time.sleep(1)  # Be respectful to RSS feeds
        
        print(f"Total articles parsed: {len(all_articles)}")
        return all_articles