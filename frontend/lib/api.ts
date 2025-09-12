import { Coin } from '@/types/coin';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchCoins(): Promise<Coin[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/coins`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store', // Always fetch fresh data
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching coins:', error);
    throw new Error('Failed to fetch coin data');
  }
}

export async function fetchCoinDetails(coinId: number) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/coins/${coinId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching coin details:', error);
    throw new Error('Failed to fetch coin details');
  }
}