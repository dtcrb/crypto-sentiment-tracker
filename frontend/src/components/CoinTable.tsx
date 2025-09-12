import { useState } from 'react';
import { Coin, SortOption } from '../types/coin';

interface CoinTableProps {
  coins: Coin[];
  loading?: boolean;
}

export default function CoinTable({ coins, loading = false }: CoinTableProps) {
  const [sortBy, setSortBy] = useState<SortOption>('sentiment');

  const getSentimentColor = (sentimentScore: number | null, noMentions: boolean) => {
    if (noMentions || sentimentScore === null) {
      return 'text-gray-500';
    }
    
    if (sentimentScore >= 0.1) {
      return 'text-green-600';
    } else if (sentimentScore <= -0.1) {
      return 'text-red-600';
    } else {
      return 'text-yellow-600';
    }
  };

  const getSentimentBgColor = (sentimentScore: number | null, noMentions: boolean) => {
    if (noMentions || sentimentScore === null) {
      return 'bg-gray-100';
    }
    
    if (sentimentScore >= 0.1) {
      return 'bg-green-50';
    } else if (sentimentScore <= -0.1) {
      return 'bg-red-50';
    } else {
      return 'bg-yellow-50';
    }
  };

  const formatSentimentScore = (score: number | null, noMentions: boolean) => {
    if (noMentions || score === null) {
      return '—';
    }
    return score.toFixed(3);
  };

  const formatPrice = (price: number | null) => {
    if (price === null) return '—';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    }).format(price);
  };

  const formatMarketCap = (marketCap: number | null) => {
    if (marketCap === null) return '—';
    
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(2)}T`;
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(2)}B`;
    } else if (marketCap >= 1e6) {
      return `$${(marketCap / 1e6).toFixed(2)}M`;
    } else {
      return `$${marketCap.toFixed(0)}`;
    }
  };

  const sortedCoins = [...coins].sort((a, b) => {
    if (sortBy === 'sentiment') {
      // Sort by sentiment score (highest first), then by market cap
      const aScore = a.no_mentions || a.sentiment_score === null ? -999 : a.sentiment_score;
      const bScore = b.no_mentions || b.sentiment_score === null ? -999 : b.sentiment_score;
      
      if (aScore !== bScore) {
        return bScore - aScore;
      }
      
      // If sentiment scores are equal, sort by market cap
      const aMarketCap = a.market_cap || 0;
      const bMarketCap = b.market_cap || 0;
      return bMarketCap - aMarketCap;
    } else {
      // Sort by market cap (highest first)
      const aMarketCap = a.market_cap || 0;
      const bMarketCap = b.market_cap || 0;
      return bMarketCap - aMarketCap;
    }
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading coin data...</span>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden">
      {/* Header with sort controls */}
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            Crypto Sentiment Tracker
          </h2>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">Sort by:</span>
            <div className="flex bg-white rounded-lg border border-gray-300 overflow-hidden">
              <button
                onClick={() => setSortBy('sentiment')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  sortBy === 'sentiment'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Sentiment
              </button>
              <button
                onClick={() => setSortBy('market_cap')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  sortBy === 'market_cap'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Market Cap
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Coin
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sentiment Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Mentions
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Market Cap
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Price (USD)
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedCoins.map((coin) => (
              <tr 
                key={coin.coin_id} 
                className={`hover:bg-gray-50 transition-colors ${getSentimentBgColor(coin.sentiment_score, coin.no_mentions)}`}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {coin.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {coin.symbol}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`text-sm font-semibold ${getSentimentColor(coin.sentiment_score, coin.no_mentions)}`}>
                    {formatSentimentScore(coin.sentiment_score, coin.no_mentions)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {coin.mentions_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatMarketCap(coin.market_cap)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatPrice(coin.price_usd)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-6 py-3 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            Showing {coins.length} cryptocurrencies
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-200 rounded"></div>
              <span>Positive</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-yellow-200 rounded"></div>
              <span>Neutral</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-200 rounded"></div>
              <span>Negative</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-gray-200 rounded"></div>
              <span>No Data</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
