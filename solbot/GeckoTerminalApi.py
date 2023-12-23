import aiohttp
import requests
from typing import Dict, List

BASE_URL = "https://api.geckoterminal.com/api/v2"

NETWORK_TOKEN_PRICE = "/simple/networks/{}/token_price/{}"
NETWORK_SUPPORTED_DEXES = "/networks/{}/dexes"
NETWORK_TRENDING_POOLS = "/networks/{}/trending_pools"
NETWORK_LATEST_POOLS = "/networks/{}/new_pools"


class GeckoTerminalApi:
    def request(self, endpoint, query_params: dict = None) -> dict:
        url = BASE_URL + endpoint
        if query_params:
            url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
        resp = requests.get(url)
        if resp.status_code != 200:
            return {}
        return resp.json()

    async def async_request(self, endpoint, query_params: dict = None) -> dict:
        url = BASE_URL + endpoint
        if query_params:
            url += "?" + "&".join(f"{k}={v}" for k, v in query_params.items())
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    def get_network_token_price(
        self, network: str, addresses: List[str]
    ) -> Dict[str, str]:
        endpoint = NETWORK_TOKEN_PRICE.format(network, ",".join(addresses))
        resp = self.request(endpoint)
        token_prices = resp["data"]["attributes"]["token_prices"]
        return token_prices

    def get_network_supported_dexes(self, network: str) -> List[str]:
        endpoint = NETWORK_SUPPORTED_DEXES.format(network)
        resp = self.request(endpoint)
        data = resp["data"]
        dexes = list(map(lambda x: x["attributes"]["name"], data))
        return dexes

    async def get_network_latest_pools(self, network: str) -> List[str]:
        endpoint = NETWORK_LATEST_POOLS.format(network)
        resp = await self.async_request(endpoint)
        latest_pools = resp["data"]
        return latest_pools

    async def get_network_trending_pools(self, network: str) -> List[dict]:
        """
        {
            "data": [
                {
                    "id": "solana_EP2ib6dYdEeqD8MfE2ezHCxX3kP3K2eLKkirfPm5eyMx",
                    "type": "pool",
                    "attributes": {
                        "base_token_price_usd": "0.1692348023957002225986155763832495612779969657520234284603419824784958",
                        "base_token_price_native_currency": "0.00175753077649918353507874",
                        "quote_token_price_usd": "96.21072492112380322196139207288649580584709566415992902",
                        "quote_token_price_native_currency": "1.0",
                        "base_token_price_quote_token": "0.00175753",
                        "quote_token_price_base_token": "568.98",
                        "address": "EP2ib6dYdEeqD8MfE2ezHCxX3kP3K2eLKkirfPm5eyMx",
                        "name": "$WIF / SOL",
                        "pool_created_at": null,
                        "fdv_usd": "169052067",
                        "market_cap_usd": "168566415.133647",
                        "price_change_percentage": {
                            "h1": "-9.61",
                            "h24": "-37.14"
                        },
                        "transactions": {
                            "h1": {
                                "buys": 1126,
                                "sells": 575,
                                "buyers": 358,
                                "sellers": 233
                            },
                            "h24": {
                                "buys": 31315,
                                "sells": 20476,
                                "buyers": 6419,
                                "sellers": 5444
                            }
                        },
                        "volume_usd": {
                            "h1": "891932.227764870690482299190838998962550811548410424653833300029755053744619508185615430787157",
                            "h24": "36843550.911314052963091856323302660063623257003283132563352927421452458821964880066116288215004558"
                        },
                        "reserve_in_usd": "2292004.5957"
                    },
                    "relationships": {
                        "base_token": {
                            "data": {
                                "id": "solana_EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
                                "type": "token"
                            }
                        },
                        "quote_token": {
                            "data": {
                                "id": "solana_So11111111111111111111111111111111111111112",
                                "type": "token"
                            }
                        },
                        "dex": {
                            "data": {
                                "id": "raydium",
                                "type": "dex"
                            }
                        }
                    }
                }, ...
            ]
        }
        """
        endpoint = NETWORK_TRENDING_POOLS.format(network)
        resp = await self.async_request(endpoint)
        trending_pools = resp["data"]
        return trending_pools

    async def get_network_pools_metadata(self, network):
        """
        [
            {
                "id": "163308983",
                "type": "pool",
                "attributes": {
                    "address": "83nS12vtpmCZ6kTpFMYVddpu7cKTDGuQm9ogXPZjvTRi",
                    "name": "DWF / SOL",
                    "from_volume_in_usd": "36219.263502404791588502356739871065292650981984163272469022960283873703420814202871663406118445",
                    "to_volume_in_usd": "36219.263502404791588502356739871065292650981984163272469022960283873703420814202871663406118445",
                    "api_address": "83nS12vtpmCZ6kTpFMYVddpu7cKTDGuQm9ogXPZjvTRi",
                    "swap_count_24h": 109655,
                    "price_percent_change": "-20.57%",
                    "price_percent_changes": {
                        "last_5m": "0%",
                        "last_15m": "0%",
                        "last_30m": "0%",
                        "last_1h": "-81.17%",
                        "last_6h": "+750.66%",
                        "last_24h": "-20.57%"
                    },
                    "pool_fee": null,
                    "base_token_id": "31176702",
                    "token_value_data": {
                        "4045901": {
                            "fdv_in_usd": 54220854279.578316,
                            "market_cap_in_usd": 0
                        },
                        "31176702": {
                            "fdv_in_usd": 8226.216076313489,
                            "market_cap_in_usd": null
                        }
                    },
                    "price_in_usd": "0.0000035787470186645913787377320873667798555122105673227102343985683",
                    "reserve_in_usd": "1.26921",
                    "aggregated_network_metrics": {
                        "total_swap_volume_usd_24h": "3272781276.783830389619723195",
                        "total_swap_volume_usd_48h_24h": "4521691208.51377946146725242",
                        "total_swap_count_24h": 5915011,
                        "total_swap_volume_percent_change_24h": "-27.6204162145881998531467234426894596538031647660050435"
                    },
                    "pool_created_at": null
                },
                "relationships": {
                    "dex": {
                        "data": {
                            "id": "699",
                            "type": "dex"
                        }
                    },
                    "tokens": {
                        "data": [
                            {
                                "id": "31176702",
                                "type": "token"
                            },
                            {
                                "id": "4045901",
                                "type": "token"
                            }
                        ]
                    },
                    "pool_metric": {
                        "data": {
                            "id": "1542378",
                            "type": "pool_metric"
                        }
                    }
                }
            }, ...
        ]
        """
        url = f"https://app.geckoterminal.com/api/p1/{network}/pools"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
                return resp["data"]

    async def get_network_trends(self, network):
        url = f"https://app.geckoterminal.com/api/p1/trends?network={network}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
                return resp["data"]

    async def get_network_top_gainers(self, network):
        """Top 10 only
         {
            "type": "top_gainers_pair",
            "address": "6KmNdS1gUatvoiREy3jrKZVS32cqsU6usE9BQhQDZZzh",
            "api_address": "6KmNdS1gUatvoiREy3jrKZVS32cqsU6usE9BQhQDZZzh",
            "price_in_usd": "0.0027760032647151361999694724203165958742116474935926211725291961561092736",
            "price_change": 0.0022052160298785847,
            "price_percent_change": 386.34641689386444,
            "network": {
                "name": "Solana",
                "image_url": "https://assets.geckoterminal.com/ttmzp815hr8hanm6bwxp549dq9rp",
                "identifier": "solana"
            },
            "dex": {
                "name": "Raydium",
                "identifier": "raydium",
                "image_url": "https://assets.geckoterminal.com/d59mdozlyr4z1w61oyqdm0xrrd2v"
            },
            "pool": {
                "pairs_count": 1
            },
            "tokens": [
                {
                    "name": "OmniCat (Wormhole)",
                    "symbol": "OMNI",
                    "image_url": "missing.png",
                    "is_base_token": true
                },
                {
                    "name": "Wrapped SOL",
                    "symbol": "SOL",
                    "image_url": "https://assets.coingecko.com/coins/images/21629/small/solana.jpg?1696520989",
                    "is_base_token": false
                }
            ],
            "pair_id": 2430537,
            "token_id": null
        },
        """
        resp = await self.get_network_trends(network)
        return resp["attributes"]["top_gainers_pairs"]

    async def get_network_dex_id_map(self, network) -> Dict[str, str]:
        url = f"https://www.geckoterminal.com/_next/data/Y70mCqdkb4Cl4BOTSPUGV/en/{network}/pools.json?network={network}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.json()
                network_dexes = resp["pageProps"]["dexes"]
                return {
                    dex_info["id"]: dex_info["attributes"]["name"]
                    for dex_info in network_dexes
                }
