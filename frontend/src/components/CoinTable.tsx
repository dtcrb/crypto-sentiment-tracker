import { useState } from 'react';
import { Coin, SortColumn, SortState } from '../types/coin';

interface CoinTableProps {
  coins: Coin[];
  loading?: boolean;
}

export default function CoinTable({ coins, loading = false }: CoinTableProps) {
  const [sortState, setSortState] = useState<SortState>({
    column: 'sentiment',
    direction: 'desc'
  });

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

  const handleSort = (column: SortColumn) => {
    setSortState(prevState => ({
      column,
      direction: prevState.column === column && prevState.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const sortedCoins = [...coins].sort((a, b) => {
    // Check if coins have no data (no mentions or null sentiment)
    const aHasNoData = a.no_mentions || a.sentiment_score === null;
    const bHasNoData = b.no_mentions || b.sentiment_score === null;

    // Always place coins without data at the bottom
    if (aHasNoData && !bHasNoData) {
      return 1; // a goes after b
    }
    if (!aHasNoData && bHasNoData) {
      return -1; // a goes before b
    }
    if (aHasNoData && bHasNoData) {
      // If both have no data, sort by market cap (highest first) as secondary sort
      const aMarketCap = a.market_cap || 0;
      const bMarketCap = b.market_cap || 0;
      return bMarketCap - aMarketCap;
    }

    // Both coins have data, proceed with normal sorting
    let aValue: number | string;
    let bValue: number | string;

    switch (sortState.column) {
      case 'sentiment':
        aValue = a.sentiment_score!; // We know it's not null due to check above
        bValue = b.sentiment_score!;
        break;
      case 'market_cap':
        aValue = a.market_cap || 0;
        bValue = b.market_cap || 0;
        break;
      case 'mentions':
        aValue = a.mentions_count;
        bValue = b.mentions_count;
        break;
      case 'price':
        aValue = a.price_usd || 0;
        bValue = b.price_usd || 0;
        break;
      case 'name':
        aValue = a.name.toLowerCase();
        bValue = b.name.toLowerCase();
        break;
      default:
        return 0;
    }

    if (aValue < bValue) {
      return sortState.direction === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortState.direction === 'asc' ? 1 : -1;
    }
    return 0;
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

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center space-x-1">
                  <span>Coin</span>
                  {sortState.column === 'name' && (
                    <span className="text-blue-600">
                      {sortState.direction === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => handleSort('sentiment')}
              >
                <div className="flex items-center space-x-1">
                  <span>Sentiment Score</span>
                  {sortState.column === 'sentiment' && (
                    <span className="text-blue-600">
                      {sortState.direction === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => handleSort('mentions')}
              >
                <div className="flex items-center space-x-1">
                  <span>Mentions</span>
                  {sortState.column === 'mentions' && (
                    <span className="text-blue-600">
                      {sortState.direction === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => handleSort('market_cap')}
              >
                <div className="flex items-center space-x-1">
                  <span>Market Cap</span>
                  {sortState.column === 'market_cap' && (
                    <span className="text-blue-600">
                      {sortState.direction === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => handleSort('price')}
              >
                <div className="flex items-center space-x-1">
                  <span>Price (USD)</span>
                  {sortState.column === 'price' && (
                    <span className="text-blue-600">
                      {sortState.direction === 'asc' ? '↑' : '↓'}
                    </span>
                  )}
                </div>
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
