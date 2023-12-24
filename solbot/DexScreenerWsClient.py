import ssl
import json
import websocket
import pandas as pd
from typing import List
from dataclasses import dataclass

WS_TRENDING = "wss://io.dexscreener.com/dex/screener/pairs/h24/1?rankBy[key]=trendingScoreH6&rankBy[order]=desc"
WS_GAINERS = "wss://io.dexscreener.com/dex/screener/pairs/h24/1?rankBy[key]=priceChangeH24&rankBy[order]=desc&filters[liquidity][min]=25000&filters[txns][h24][min]=50&filters[volume][h24][min]=10000"
WS_NEWEST = "wss://io.dexscreener.com/dex/screener/pairs/h24/1?rankBy[key]=volume&rankBy[order]=desc&filters[pairAge][max]=24"


@dataclass
class DexScreenerPair:
    chain: str
    dex: str
    pair_address: str
    base_token_symbol: str
    base_token_name: str
    base_token_address: str
    quote_token_symbol: str
    quote_token_name: str
    quote_token_address: str
    pair_create_timestamp: float

    # base token parameters
    price_usd: str
    market_cap: float
    volumn_5m: float
    volumn_1h: float
    volumn_6h: float
    volumn_24h: float
    price_change_5m: float
    price_change_1h: float
    price_change_6h: float
    price_change_24h: float

    @staticmethod
    def from_dict(obj: dict) -> "DexScreenerPair":
        try:
            return DexScreenerPair(
                chain=obj["chainId"],
                dex=obj["dexId"],
                pair_address=obj["pairAddress"],
                base_token_symbol=obj["baseToken"]["symbol"],
                base_token_name=obj["baseToken"]["name"],
                base_token_address=obj["baseToken"]["address"],
                quote_token_symbol=obj["quoteToken"]["symbol"],
                quote_token_name=obj["quoteToken"]["name"],
                quote_token_address=obj["quoteToken"]["address"],
                pair_create_timestamp=obj["chainId"],
                price_usd=obj.get("priceUsd"),
                market_cap=obj.get("marketCap"),
                volumn_5m=obj["volume"].get("m5"),
                volumn_1h=obj["volume"].get("h1"),
                volumn_6h=obj["volume"].get("h6"),
                volumn_24h=obj["volume"].get("h24"),
                price_change_5m=obj["priceChange"].get("m5"),
                price_change_1h=obj["priceChange"].get("h1"),
                price_change_6h=obj["priceChange"].get("h6"),
                price_change_24h=obj["priceChange"].get("h24"),
            )
        except:
            print(obj)

    @staticmethod
    def dicts_to_list(objs: List[dict]) -> List["DexScreenerPair"]:
        return list(map(DexScreenerPair.from_dict, objs))


class DexScreenerWsClient:
    MAX_TRIES = 5

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
            "Origin": "https://dexscreener.com",
        }

    def subscribe_and_recv(self, uri) -> dict:
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.connect(uri, header=self.get_header(), suppress_origin=True)
        return json.loads(ws.recv())

    def get_pairs(self, uri):
        for i in range(self.MAX_TRIES):
            data = self.subscribe_and_recv(uri)
            if pairs := data.get("pairs"):
                return pairs
            print(f"[{self.__class__.__name__}] ({i + 1}/{self.MAX_TRIES}) -- {data}")
        return []

    @staticmethod
    def filter_chain_pairs(pairs: list, chain: str):
        return list(filter(lambda x: x["chainId"] == chain, pairs))

    def get_trending_pairs(self, chain: str = None):
        pairs = self.get_pairs(WS_TRENDING)
        if chain:
            pairs = self.filter_chain_pairs(pairs, chain)
        return pairs

    def get_top_gaining_pairs(self, chain: str = None):
        pairs = self.get_pairs(WS_GAINERS)
        if chain:
            pairs = self.filter_chain_pairs(pairs, chain)
        return pairs

    def get_newest_pairs(self, chain: str = None):
        pairs = self.get_pairs(WS_NEWEST)
        if chain:
            pairs = self.filter_chain_pairs(pairs, chain)
        return pairs


def main():
    dex_screener_ws_client = DexScreenerWsClient()
    trending_pairs = dex_screener_ws_client.get_trending_pairs(chain="solana")
    top_gaining_pairs = dex_screener_ws_client.get_top_gaining_pairs(chain="solana")
    newest_pairs = dex_screener_ws_client.get_newest_pairs(chain="solana")

    trending_pairs_df = pd.DataFrame(DexScreenerPair.dicts_to_list(trending_pairs))
    top_gaining_pairs_df = pd.DataFrame(
        DexScreenerPair.dicts_to_list(top_gaining_pairs)
    )
    newest_pairs_df = pd.DataFrame(DexScreenerPair.dicts_to_list(newest_pairs))

    print("Trending Pairs")
    print(trending_pairs_df.head(n=10))
    print("Top Gaining Pairs")
    print(top_gaining_pairs_df.head(n=10))
    print("Newest Pairs")
    print(newest_pairs_df.head(n=10))


if __name__ == "__main__":
    main()
