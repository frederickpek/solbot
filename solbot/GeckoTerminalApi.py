import aiohttp
import requests
from typing import Dict, List

BASE_URL = "https://api.geckoterminal.com/api/v2"
BASE_URL_INNER = "https://app.geckoterminal.com/api/p1"

# public endpoints
NETWORK_TOKEN_PRICE = "/simple/networks/{}/token_price/{}"
NETWORK_SUPPORTED_DEXES = "/networks/{}/dexes"
NETWORK_TRENDING_POOLS = "/networks/{}/trending_pools"
NETWORK_LATEST_POOLS = "/networks/{}/new_pools"

# inner endpoints
NETWORK_ALL_POOLS = "/{}/pools"
NETWORK_POOL = "/{}/pools/{}"


class GeckoTerminalApi:
    def request(self, base_url, endpoint, query_params: dict = None) -> dict:
        url = base_url + endpoint
        if query_params:
            url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
        resp = requests.get(url)
        if resp.status_code != 200:
            return {}
        return resp.json()

    async def async_request(
        self, base_url, endpoint, query_params: dict = None
    ) -> dict:
        url = base_url + endpoint
        if query_params:
            url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    def get_network_token_price(
        self, network: str, addresses: List[str]
    ) -> Dict[str, str]:
        endpoint = NETWORK_TOKEN_PRICE.format(network, ",".join(addresses))
        resp = self.request(BASE_URL, endpoint)
        token_prices = resp["data"]["attributes"]["token_prices"]
        return token_prices

    def get_network_supported_dexes(self, network: str) -> List[str]:
        endpoint = NETWORK_SUPPORTED_DEXES.format(network)
        resp = self.request(BASE_URL, endpoint)
        data = resp["data"]
        dexes = list(map(lambda x: x["attributes"]["name"], data))
        return dexes

    async def get_network_latest_pools(self, network: str) -> List[str]:
        endpoint = NETWORK_LATEST_POOLS.format(network)
        resp = await self.async_request(BASE_URL, endpoint)
        latest_pools = resp["data"]
        return latest_pools

    async def get_network_trending_pools(self, network: str) -> List[dict]:
        endpoint = NETWORK_TRENDING_POOLS.format(network)
        resp = await self.async_request(BASE_URL, endpoint)
        trending_pools = resp["data"]
        return trending_pools

    async def get_network_all_pools(
        self,
        network: str,
        page: int = None,
        include_network_metrics: bool = None,
        include: str = None,
    ) -> List[dict]:
        query_params = {}
        if page:
            query_params["page"] = page
        if include:
            query_params["include"] = ",".join(
                [
                    "dex",
                    "dex.network",
                    "dex.network.network_metric",
                    "tokens",
                ]
            )
        if include_network_metrics:
            query_params["include_network_metrics"] = "true"
        endpoint = NETWORK_ALL_POOLS.format(network)
        resp = await self.async_request(
            BASE_URL_INNER, endpoint, query_params=query_params
        )
        return resp

    async def get_network_pool(
        self, network: str, address: str, include: str = None
    ) -> Dict:
        query_params = {}
        if include:
            query_params["include"] = ",".join(
                [
                    "dex",
                    "dex.network.explorers",
                    "dex_link_services",
                    "network_link_services",
                    "pairs",
                    "token_link_services",
                    "tokens.token_security_metric",
                ]
            )
        endpoint = NETWORK_POOL.format(network, address)
        resp = await self.async_request(
            BASE_URL_INNER, endpoint, query_params=query_params
        )
        return resp
