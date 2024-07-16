import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
from typing import List, Dict

BASE_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

class CurrencyRateFetcher:
    def __init__(self, days: int):
        self.days = days if days <= 10 else 10
        self.session = aiohttp.ClientSession()

    async def fetch_rate_for_date(self, date: str) -> Dict:
        url = f"{BASE_URL}{date}"
        async with self.session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return self.parse_rate(data)
            else:
                print(f"Failed to fetch data for {date}: {response.status}")
                return {}

    def parse_rate(self, data: Dict) -> Dict:
        date = data['date']
        rates = {rate['currency']: {'sale': rate['saleRate'], 'purchase': rate['purchaseRate']} for rate in data['exchangeRate'] if rate['currency'] in ['EUR', 'USD']}
        return {date: rates}

    async def fetch_rates(self) -> List[Dict]:
        tasks = []
        for i in range(self.days):
            date = (datetime.now() - timedelta(days=i+1)).strftime('%d.%m.%Y')
            tasks.append(self.fetch_rate_for_date(date))
        return await asyncio.gather(*tasks)

    async def close_session(self):
        await self.session.close()

async def main(days: int):
    fetcher = CurrencyRateFetcher(days)
    try:
        rates = await fetcher.fetch_rates()
        print([rate for rate in rates if rate])
    finally:
        await fetcher.close_session()

if __name__ == '__main__':
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: py main.py <number_of_days>")
        sys.exit(1)
    days = int(sys.argv[1])
    asyncio.run(main(days))