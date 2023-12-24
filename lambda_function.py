import time
import logging
import traceback
import pandas as pd
from datetime import datetime

from solbot.secret import (
    LARK_KEY,
    LARK_KEY_ERROR,
)
from solbot.utils import format_number
from solbot.YFinanceApi import YFinanceApi
from solbot.LarkClient import (
    LarkClient,
    HREF,
    GREY,
    RED,
    GREEN,
    HORIZONTAL_LINE_ELEMENT,
)
from solbot.DexScreenerWsClient import (
    DexScreenerWsClient,
    DexScreenerPair,
)

SOLSCAN_URL = "https://solscan.io/account/"
DEX_SCREENER = "DexScreener"
TOP_GAINING_POOLS_LINK = "https://dexscreener.com/solana?rankBy=priceChangeH24&order=desc&minLiq=25000&min24HTxns=50&min24HVol=10000"
TRENDING_POOLS_LINK = "https://dexscreener.com/solana?rankBy=trendingScoreH6&order=desc"
NEWEST_POOLS_LINK = "https://dexscreener.com/solana?rankBy=volume&order=desc&maxAge=24"


def main():
    sol_usd = YFinanceApi.get_sol_usd_price()
    dex_screener_ws_client = DexScreenerWsClient()
    trending_pairs = dex_screener_ws_client.get_trending_pairs(chain="solana")
    top_gaining_pairs = dex_screener_ws_client.get_top_gaining_pairs(chain="solana")
    newest_pairs = dex_screener_ws_client.get_newest_pairs(chain="solana")

    interval_map = {"5m", "1h", "6h", "24h"}

    def price_change_formatter(price_change):
        if price_change is None:
            return GREY("-")
        color_fmt = GREY if price_change == 0 else RED if price_change < 0 else GREEN
        return color_fmt(f"{price_change:,}" + "%")

    row_elem_formatters = {x: price_change_formatter for x in interval_map}

    def pair_link_seedling(pair_name: str, link: str, create_timestamp: float):
        create_timestamp = create_timestamp or 0
        seed = ""
        H = 3600000
        diff = time.time() * 1000 - create_timestamp
        if diff < 24 * H:
            hours = int(diff / H)
            seed = f" ({GREEN(str(hours) + 'h')})"
        return HREF(pair_name, link) + seed

    #### SOLANA STATUS ####

    dt = datetime.now().strftime("%d %B %Y")
    header = f"Sol Bot Daily - {dt}"
    header_element = LarkClient.generate_header_element(header, "wathet")
    sol_status = (
        f"*P.S. SOL (${sol_usd:,.2f}) is but a {1000/sol_usd:.1f}x away from 1000🔥*"
    )
    sol_status_element = LarkClient.generate_markdown_element(sol_status)

    #### TRENDING POOLS ####

    i = 1
    N = 3
    trending_pair_elements = []
    ranks = {1: "🥇", 2: "🥈", 3: "🥉"}
    for pair in trending_pairs:
        dex_screener_pair = DexScreenerPair.from_dict(pair)

        pair_name = (
            dex_screener_pair.base_token_symbol
            + "/"
            + dex_screener_pair.quote_token_symbol
        )
        link = SOLSCAN_URL + dex_screener_pair.pair_address
        pool = pair_link_seedling(
            pair_name, link, dex_screener_pair.pair_create_timestamp
        )

        pair_info = [
            f"**{ranks.get(i, i)}: {pool}**",
            f"**Dex**: {dex_screener_pair.dex.title()}",
            f"**Vol24h**: ${float(dex_screener_pair.volumn_24h or 0):,.2f}",
            f"**MarketCap**: ${format_number(dex_screener_pair.market_cap)}",
            f"**{dex_screener_pair.base_token_symbol}/USD**: ${format_number(dex_screener_pair.price_usd)}",
        ]

        pair_price_changes_info = {
            "5m": dex_screener_pair.price_change_5m,
            "1h": dex_screener_pair.price_change_1h,
            "6h": dex_screener_pair.price_change_6h,
            "24h": dex_screener_pair.price_change_24h,
        }

        pair_price_changes_df = pd.DataFrame([pair_price_changes_info])
        pair_price_changes_element = LarkClient.generate_table_element(
            pair_price_changes_df, row_elem_formatters=row_elem_formatters
        )

        pair_info_element = LarkClient.generate_markdown_element("\n".join(pair_info))
        trending_pair_elements.extend([pair_info_element, pair_price_changes_element])

        i += 1
        if i > N:
            break

    trending_pairs_title = (
        f"**🔥 Trending Pools** - {GREY(HREF(DEX_SCREENER, TRENDING_POOLS_LINK))}"
    )
    trending_pairs_title_element = LarkClient.generate_markdown_element(
        trending_pairs_title
    )

    #### TOP GAINERS ####

    top_gainers = []
    for pair in top_gaining_pairs[:5]:
        dex_screener_pair = DexScreenerPair.from_dict(pair)
        pair_name = (
            dex_screener_pair.base_token_symbol
            + "/"
            + dex_screener_pair.quote_token_symbol
        )
        link = SOLSCAN_URL + dex_screener_pair.pair_address
        pool = pair_link_seedling(
            pair_name, link, dex_screener_pair.pair_create_timestamp
        )
        top_gainers.append(
            {
                "Pool": pool,
                "Dex": dex_screener_pair.dex.title(),
                "24h": dex_screener_pair.price_change_24h,
            }
        )

    top_gainers_title = (
        f"**🚀 Top Gainers** - {GREY(HREF(DEX_SCREENER, TOP_GAINING_POOLS_LINK))}"
    )
    top_gainers_title_element = LarkClient.generate_markdown_element(top_gainers_title)
    top_gainers_df = pd.DataFrame(top_gainers)
    top_gainers_element = LarkClient.generate_table_element(
        top_gainers_df, row_elem_formatters=row_elem_formatters, width="auto"
    )

    #### LATEST POOLS ####

    latest_pools = []
    for pair in newest_pairs[:5]:
        dex_screener_pair = DexScreenerPair.from_dict(pair)
        pair_name = (
            dex_screener_pair.base_token_symbol
            + "/"
            + dex_screener_pair.quote_token_symbol
        )
        link = SOLSCAN_URL + dex_screener_pair.pair_address
        pool = pair_link_seedling(
            pair_name, link, dex_screener_pair.pair_create_timestamp
        )
        latest_pools.append(
            {
                "Pool": pool,
                "Dex": dex_screener_pair.dex.title(),
                "24h": dex_screener_pair.price_change_24h,
            }
        )

    latest_pools_title = (
        f"**🔍 Latest Pools** - {GREY(HREF(DEX_SCREENER, NEWEST_POOLS_LINK))}"
    )
    latest_pools_title_element = LarkClient.generate_markdown_element(
        latest_pools_title
    )
    latest_pools_df = pd.DataFrame(latest_pools)
    latest_pools_element = LarkClient.generate_table_element(
        latest_pools_df, row_elem_formatters=row_elem_formatters, width="auto"
    )

    elements = [
        trending_pairs_title_element,
        *trending_pair_elements,
        HORIZONTAL_LINE_ELEMENT,
        top_gainers_title_element,
        top_gainers_element,
        HORIZONTAL_LINE_ELEMENT,
        latest_pools_title_element,
        latest_pools_element,
        HORIZONTAL_LINE_ELEMENT,
        sol_status_element,
    ]

    lark_client = LarkClient(key=LARK_KEY)
    lark_client.send_card(header=header_element, elements=elements)


def lambda_handler(event=None, context=None):
    for _ in range(3):
        try:
            main()
            return {"statusCode": 200}
        except Exception as err:
            error_msg = f"{err}\n{traceback.format_exc()}"
            logging.error(error_msg)
            LarkClient(key=LARK_KEY_ERROR).send_message(error_msg)
    return {"statusCode": 500}


if __name__ == "__main__":
    lambda_handler()
