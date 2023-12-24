import aiohttp
import requests

BASE_URL = "https://query2.finance.yahoo.com/v8/finance/chart/"


class YFinanceApi:
    @staticmethod
    def get_header():
        return {
            "User-Agent": " ".join(
                [
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                    "AppleWebKit/537.36 (KHTML, like Gecko)"
                    "Chrome/113.0.0.0 Safari/537.36",
                ]
            ),
            "Origin": "https://query2.finance.yahoo.com",
        }

    @staticmethod
    def get_default_params():
        return {
            "range": "1m",
            "interval": "1d",
            "includePrePost": "false",
            "events": "div,splits,capitalGains",
        }

    @staticmethod
    async def async_get_yfinance_chart(ticker) -> dict:
        params = YFinanceApi.get_default_params()
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL + ticker, params=params) as response:
                return await response.json()

    @staticmethod
    async def async_get_yfinance_ticker_price(ticker) -> float:
        data = await YFinanceApi.async_get_yfinance_chart(ticker=ticker)
        return data["chart"]["result"][0]["meta"]["regularMarketPrice"]

    @staticmethod
    async def async_get_sol_usd_price() -> float:
        return await YFinanceApi.async_get_yfinance_ticker_price(ticker="SOL-USD")

    @staticmethod
    def get_yfinance_chart(ticker) -> dict:
        headers = YFinanceApi.get_header()
        params = YFinanceApi.get_default_params()
        response = requests.get(BASE_URL + ticker, params=params, headers=headers)
        return response.json()

    @staticmethod
    def get_yfinance_ticker_price(ticker) -> float:
        data = YFinanceApi.get_yfinance_chart(ticker=ticker)
        return data["chart"]["result"][0]["meta"]["regularMarketPrice"]

    @staticmethod
    def get_sol_usd_price() -> float:
        return YFinanceApi.get_yfinance_ticker_price(ticker="SOL-USD")
