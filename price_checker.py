import aiohttp
import asyncio
from typing import Optional, Dict
from datetime import datetime, timedelta
import config


class PriceChecker:
    def __init__(self):
        self.session = None
        self.valid_symbols_cache = set()

    async def init_session(self):
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
        """
        Get current stock price from Vietstock API
        """
        try:
            await self.init_session()

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

            print(f"🔍 DEBUG: Requesting Vietstock API for {symbol}")
            print(f"🔍 DEBUG: URL = {url}")
            print(f"🔍 DEBUG: Params = {params}")

            async with self.session.get(url, params=params, timeout=10) as response:
                print(f"🔍 DEBUG: Response status = {response.status}")

                if response.status == 200:
                    data = await response.json()
                    print(f"🔍 DEBUG: Response keys = {data.keys() if isinstance(data, dict) else 'Not a dict'}")

                    # Vietstock returns: {c: [prices], o: [opens], h: [highs], l: [lows], v: [volumes], t: [timestamps]}
                    if data and 'c' in data and len(data['c']) > 0:
                        # Get the latest closing price (last item in array)
                        latest_price = data['c'][-1]
                        print(f"🔍 DEBUG: Extracted price = {latest_price}")

                        if latest_price:
                            return float(latest_price)  # Already in thousands
                    else:
                        print(f"🔍 DEBUG: No price data in response")
                        print(f"🔍 DEBUG: Full response = {data}")
                else:
                    text = await response.text()
                    print(f"🔍 DEBUG: Error response: {text[:200]}")

                return None
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a stock symbol is valid
        """
        price = await self.get_price(symbol)
        return price is not None

    async def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed stock information from Vietstock API
        """
        try:
            await self.init_session()

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
