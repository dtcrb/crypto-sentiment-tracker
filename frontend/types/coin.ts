export interface Coin {
  coin_id: number;
  coingecko_id: string;
  symbol: string;
  name: string;
  price_usd: number | null;
  market_cap: number | null;
  sentiment_score: number | null;
  mentions_count: number;
  no_mentions: boolean;
}

export type SortOption = 'sentiment' | 'market_cap';

export interface ApiResponse {
  coins: Coin[];
  last_updated?: string;
}