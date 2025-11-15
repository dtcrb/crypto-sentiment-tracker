// Mock the env module before importing api
jest.mock('./env', () => ({
  API_BASE_URL: 'http://localhost:8000',
}));

import { fetchCoins, fetchCoinDetails, fetchCoinArticles } from './api';
import type { Coin } from '../types/coin';

describe('API lib', () => {
  beforeEach(() => {
    (global as any).fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('fetchCoins', () => {
    it('returns coins on success', async () => {
      const coins: Coin[] = [
        {
          coin_id: 1,
          coingecko_id: 'bitcoin',
          symbol: 'BTC',
          name: 'Bitcoin',
          price_usd: 50000,
          market_cap: 900000000000,
          sentiment_score: 0.8,
          mentions_count: 1000,
          no_mentions: false,
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValueOnce(coins),
      } as any);

      const result = await fetchCoins();
      expect(result).toEqual(coins);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/coins$/),
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('throws a friendly error on non-OK response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({ ok: false, status: 500 } as any);
      await expect(fetchCoins()).rejects.toThrow('Failed to fetch coin data');
    });
  });

  describe('fetchCoinDetails', () => {
    it('returns coin details on success', async () => {
      const coinDetail = {
        coin_id: 1,
        name: 'Bitcoin',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValueOnce(coinDetail),
      } as any);

      const result = await fetchCoinDetails(1);
      expect(result).toEqual(coinDetail);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/coins\/1$/),
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('throws a friendly error on non-OK response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({ ok: false, status: 404 } as any);
      await expect(fetchCoinDetails(123)).rejects.toThrow('Failed to fetch coin details');
    });
  });

  describe('fetchCoinArticles', () => {
    it('returns article summaries on success', async () => {
      const payload = [
        { id: 1, title: 'A', summary: 's', link: 'http://a', published_date: '2024-01-01T00:00:00Z' },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: jest.fn().mockResolvedValueOnce(payload),
      } as any);

      const result = await fetchCoinArticles(42, 10);
      expect(result).toEqual(payload);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/coins\/42\/articles\?limit=10$/),
        expect.objectContaining({ method: 'GET' })
      );
    });

    it('throws a friendly error on non-OK response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({ ok: false, status: 500 } as any);
      await expect(fetchCoinArticles(1)).rejects.toThrow('Failed to fetch coin articles');
    });
  });
});
