import { useEffect, useState } from 'react';
import CoinTable from './components/CoinTable';
import { fetchCoins } from './lib/api';
import { Coin } from './types/coin';

function App() {
  const [coins, setCoins] = useState<Coin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    const loadCoins = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchCoins();
        setCoins(data);
        setLastUpdated(new Date().toLocaleString());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    loadCoins();
  }, []);


  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            24 Hour Crypto Sentiment Tracker
          </h1>
          <p className="text-gray-600 mt-2">
            Real-time cryptocurrency sentiment analysis based on news sources
          </p>
          {lastUpdated && (
            <p className="text-sm text-gray-500 mt-2">
              Last updated: {lastUpdated}
            </p>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error loading data
                </h3>
                <p className="text-sm text-red-700 mt-1">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <CoinTable coins={coins} loading={loading} />

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Data sourced from CoinGecko API and analyzed from major crypto news outlets.
          </p>
          <p className="mt-1">
            Sentiment analysis powered by VADER (Valence Aware Dictionary and sEntiment Reasoner).
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
