import asyncio
import pandas as pd
from datetime import datetime
from solbot.Ticker import get_sol_usd_price
from solbot.LarkClient import (
    LarkClient,
    GREY,
    RED,
    GREEN,
    HORIZONTAL_LINE_ELEMENT,
)
from solbot.GeckoTerminalApi import GeckoTerminalApi
from solbot.utils import format_number, price_percent_change_to_float
from solbot.secret import LARK_KEY


def lambda_handler(event=None, context=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    gecko_terminal_api = GeckoTerminalApi()

    (
        sol_usd,
        solana_trending_pools,
        solana_pools_metadata,
        solana_dex_id_map,
        solana_latest_pools,
    ) = loop.run_until_complete(
        asyncio.gather(
            get_sol_usd_price(),
            gecko_terminal_api.get_network_trending_pools("solana"),
            gecko_terminal_api.get_network_pools_metadata("solana"),
            gecko_terminal_api.get_network_dex_id_map("solana"),
            gecko_terminal_api.get_network_latest_pools("solana"),
        )
    )

    dt = datetime.now().strftime("%d %B %Y")
    header = f"Sol Bot Daily - {dt}"
    header_element = LarkClient.generate_header_element(header, "wathet")

    sol_status = (
        f"*P.S. SOL (${sol_usd:,.2f}) is but a {1000/sol_usd:.1f}x away from 1000🔥*"
    )
    sol_status_element = LarkClient.generate_markdown_element(sol_status)

    interval_map = {
        "5m": "last_5m",
        "1h": "last_1h",
        "6h": "last_6h",
        "24h": "last_24h",
    }

    def price_change_formatter(price_change):
        _m = {"+": GREEN, "-": RED}
        sign = price_change[0]
        color_fmt = _m.get(sign, GREY)
        return color_fmt(price_change)

    row_elem_formatters = {x: price_change_formatter for x in interval_map.keys()}

    solana_pools_metadata = {
        data["attributes"]["address"]: data for data in solana_pools_metadata
    }

    # TRENDING POOLS

    rem = 5
    pool_elements = []
    ranks = {1: "🥇", 2: "🥈", 3: "🥉"}
    solscan_url = "https://solscan.io/account/"
    for i, pool in enumerate(solana_trending_pools):
        if not rem:
            break
        attributes = pool["attributes"]
        base_token_price_usd = attributes["base_token_price_usd"]
        pool_name = attributes["name"]
        base_token, _ = pool_name.split(" / ")
        fdv_usd = attributes["fdv_usd"]
        volume_usd_h24 = attributes["volume_usd"]["h24"]
        relationships = pool["relationships"]
        dex_id = relationships["dex"]["data"]["id"]
        address = attributes["address"]
        pool_info = [
            f"**{ranks.get(i + 1, i + 1)}: [{pool_name}]({solscan_url + address})**",
            f"**Dex**: {dex_id.title()}",
            f"**Vol24h**: ${float(volume_usd_h24):,.2f}",
            f"**FDV**: ${format_number(fdv_usd)}",
            f"**{base_token}-USD**: ${format_number(base_token_price_usd)}",
        ]
        pool_metadata = solana_pools_metadata.get(address)
        if not pool_metadata:
            continue

        pool_price_changes_info = {
            k: pool_metadata["attributes"]["price_percent_changes"][v]
            for k, v in interval_map.items()
        }

        pool_price_changes_df = pd.DataFrame([pool_price_changes_info])
        pool_price_changes_element = LarkClient.generate_table_element(
            pool_price_changes_df, row_elem_formatters=row_elem_formatters
        )

        pool_info_element = LarkClient.generate_markdown_element("\n".join(pool_info))
        pool_elements.extend([pool_info_element, pool_price_changes_element])
        rem -= 1

    pools_title = "**Trending Dex Pairs 🔥**\n<font color='grey'>Brought to you by GeckoTerminal</font>"
    pools_title_element = LarkClient.generate_markdown_element(pools_title)

    solana_pools_metadata_list = [
        (
            price_percent_change_to_float(
                metadata["attributes"]["price_percent_change"]
            ),
            metadata,
        )
        for _, metadata in solana_pools_metadata.items()
    ]
    solana_pools_metadata_list.sort(key=lambda x: x[0], reverse=True)

    # TOP GAINERS

    top_gainers = []
    pool_to_address = {}
    for _, data in solana_pools_metadata_list[:10]:
        pool = data["attributes"]["name"]
        top_gainers.append(
            {
                "Pool": pool,
                "Dex": solana_dex_id_map.get(
                    data["relationships"]["dex"]["data"]["id"], "?"
                ),
                "24h": data["attributes"]["price_percent_change"],
            }
        )
        address = data["attributes"]["address"]
        pool_to_address[pool] = address

    def link_pools(pool):
        address = pool_to_address[pool]
        return f"[{pool}]({solscan_url + address})"

    top_gainers_title = "**Top Gainers 🚀**"
    top_gainers_title_element = LarkClient.generate_markdown_element(top_gainers_title)
    top_gainers_df = pd.DataFrame(top_gainers)
    row_elem_formatters.update({"Pool": link_pools})
    top_gainers_element = LarkClient.generate_table_element(
        top_gainers_df, row_elem_formatters=row_elem_formatters
    )

    # LATEST POOLS

    latest_pools = []
    for pool_info in solana_latest_pools[:10]:
        dex = pool_info["relationships"]["dex"]["data"]["id"]
        pool = pool_info["attributes"]["name"]
        address = pool_info["attributes"]["address"]
        pool_to_address[pool] = address
        latest_pools.append(
            {
                "Pool": pool,
                "Dex": dex,
            }
        )

    latest_pools_title = "**Latest Pools 🔍**"
    latest_pools_title_element = LarkClient.generate_markdown_element(
        latest_pools_title
    )
    latest_pools_df = pd.DataFrame(latest_pools)
    latest_pools_element = LarkClient.generate_table_element(
        latest_pools_df, row_elem_formatters=row_elem_formatters
    )

    elements = [
        pools_title_element,
        *pool_elements,
        HORIZONTAL_LINE_ELEMENT,
        top_gainers_title_element,
        top_gainers_element,
        HORIZONTAL_LINE_ELEMENT,
    ]

    if latest_pools:
        elements.append(latest_pools_title_element)
        elements.append(latest_pools_element)
        elements.append(HORIZONTAL_LINE_ELEMENT)

    elements.append(sol_status_element)

    lark_client = LarkClient(key=LARK_KEY)
    resp = lark_client.send_card(header=header_element, elements=elements)
    print(f"[lambda_function] -- {resp.text}")

    return {"statusCode": 200}


if __name__ == "__main__":
    lambda_handler()
