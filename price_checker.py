import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import aiohttp

import config


class PriceChecker:
    def __init__(self):
        self.session = None
        self.valid_symbols_cache = set()

    def init_session(self):
        """Initialize aiohttp session with headers"""
        if self.session is None:
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'en,en-US;q=0.9,vi;q=0.8',
                'Origin': 'https://stockchart.vietstock.vn',
                'Referer': 'https://stockchart.vietstock.vn/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            }
            self.session = aiohttp.ClientSession(headers=headers)

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    async def get_price(self, symbol: str) -> Optional[float]:
        """Get current stock price from Vietstock API"""
        try:
            self.init_session()

            # Vietstock API endpoint
            url = config.VIETSTOCK_API_URL

            # Get last 2 days of data
            to_timestamp = int(datetime.now().timestamp())
            from_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

            params = {
                'symbol': symbol.upper(),
                'resolution': '1D',
                'from': from_timestamp,
                'to': to_timestamp,
                'countback': 7
            }

            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    # Vietstock returns: {c: [prices], o: [opens], h: [highs], l: [lows], v: [volumes], t: [timestamps]}
                    if data and 'c' in data and len(data['c']) > 0:
                        # Get the latest closing price (last item in array)
                        latest_price = data['c'][-1]

                        if latest_price:
                            return float(latest_price)  # Already in thousands
                    else:
                        print(f"🔍 DEBUG: Full response = {data}")
                else:
                    text = await response.text()
                    print(f"🔍 DEBUG: Error response: {text[:200]}")

                return None
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None

    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get prices for multiple symbols efficiently using parallel request"""
        if not symbols:
            return {}

        self.init_session()

        # Remove duplicates and convert to uppercase
        unique_symbols = list(set([s.upper() for s in symbols]))

        print(f"🔄 Fetching prices for {len(unique_symbols)} symbols in parallel...")

        # Create tasks for parallel execution
        tasks = [self.get_price(symbol) for symbol in unique_symbols]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=15.0  # Max 15s cho toàn bộ batch
            )
        except asyncio.TimeoutError:
            print(f"⚠️  Batch fetch timeout after 15s")
            return {}

        # Build result dictionary
        prices = {}
        success_count = 0
        for symbol, result in zip(unique_symbols, results):
            if not isinstance(result, Exception) and result is not None:
                prices[symbol] = result
                success_count += 1
            else:
                error_msg = str(result) if isinstance(result, Exception) else 'No data'
                print(f"⚠️  Failed to get price for {symbol}: {error_msg}")

        print(f"✅ Successfully fetched {success_count}/{len(unique_symbols)} prices")
        return prices

    async def validate_symbol(self, symbol: str) -> bool:
        """Check if a stock symbol is valid"""
        price = await self.get_price(symbol)
        return price is not None

    async def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get detailed stock information from Vietstock API"""
        try:
            self.init_session()

            url = config.VIETSTOCK_API_URL

            to_timestamp = int(datetime.now().timestamp())
            from_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

            params = {
                'symbol': symbol.upper(),
                'resolution': '1D',
                'from': from_timestamp,
                'to': to_timestamp,
                'countback': 7
            }

            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()

                    # Vietstock format: {c: close, o: open, h: high, l: low, v: volume, t: time}
                    if data and 'c' in data and len(data['c']) > 0:
                        # Get latest data (last item in each array)
                        close_price = data['c'][-1]
                        open_price = data['o'][-1]
                        high_price = data['h'][-1]
                        low_price = data['l'][-1]
                        volume = data['v'][-1]

                        # Calculate change
                        change = close_price - open_price
                        change_percent = (change / open_price * 100) if open_price else 0

                        return {
                            'symbol': symbol.upper(),
                            'price': float(close_price),
                            'change': float(change),
                            'change_percent': float(change_percent),
                            'volume': int(volume),
                            'high': float(high_price),
                            'low': float(low_price),
                        }
                return None
        except Exception as e:
            print(f"Error getting info for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
