# Example script to for deploying a perp dex
#
# IMPORTANT: Replace any arguments for the exchange calls below to match your deployment requirements.

import argparse
from examples import example_utils

from hyperliquid.utils import constants

# Set to True to register a new perp dex.
REGISTER_PERP_DEX = True

# Mainnet config
MAINNET_CONFIG = {
    "name": "HyENA",
    "collateralToken": 235,  # USDe
    "oracle_updater": "0x58e1b0e63c905d5982324fcd9108582623b8132e",
    "markets": [
        {"name": "BTC", "szDecimals": 5, "maxLeverage": 40, "marginTableId": 56},
        {"name": "ETH", "szDecimals": 4, "maxLeverage": 25, "marginTableId": 55},
        {"name": "SOL", "szDecimals": 2, "maxLeverage": 20, "marginTableId": 54},
    ],
}

# Testnet config
TESTNET_CONFIG = {
    "name": "test22",
    "collateralToken": 1255,  # USDe
    "oracle_updater": "0xe92d5afedaf9eab98a70b7b0118b7187c1292c5c",
    "markets": [
        {"name": "BTC", "szDecimals": 5, "maxLeverage": 40, "marginTableId": 54},
        {"name": "ETH", "szDecimals": 4, "maxLeverage": 25, "marginTableId": 53},
        {"name": "SOL", "szDecimals": 2, "maxLeverage": 10, "marginTableId": 10},
    ],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mainnet",
        action="store_true",
        help="Use mainnet config instead of testnet",
    )
    args = parser.parse_args()

    if args.mainnet:
        config = MAINNET_CONFIG
        api_url = constants.MAINNET_API_URL
        print("Using mainnet config")
    else:
        config = TESTNET_CONFIG
        api_url = constants.TESTNET_API_URL
        print("Using testnet config")

    _, info, exchange = example_utils.setup(api_url, skip_ws=True)

    # We need to get oracle prices for the base assets from the main Hyperliquid dex
    # to use as initial oracle prices for our new perp dex.
    meta, asset_ctxs = info.meta_and_asset_ctxs()
    oracle_pxs = {}
    market_names = [m["name"] for m in config["markets"]]
    for i, asset_meta in enumerate(meta["universe"]):
        asset_name = asset_meta["name"]
        if asset_name in market_names:
            oracle_pxs[asset_name] = asset_ctxs[i]["oraclePx"]
            print(f"Found oracle price for {asset_name}: {oracle_pxs[asset_name]}")

    dex_name = config["name"]
    print(f"Preparing to deploy dex '{dex_name}'")

    # Step 1: Registering a Perp Dex and Assets
    # This needs to be done once per asset.
    # The first asset registration for a new dex name will also register the dex.

    perp_dex_schema_input = {
        "fullName": f"{dex_name} dex",
        "collateralToken": config["collateralToken"],
        "oracleUpdater": config["oracle_updater"],
    }

    for i, market in enumerate(config["markets"]):
        market_name = market["name"]
        print(f"Registering market {market_name} on dex {dex_name}")

        schema = None
        if i == 0 and REGISTER_PERP_DEX:
            schema = perp_dex_schema_input

        if market_name not in oracle_pxs:
            print(f"Error: Could not find oracle price for {market_name}. Skipping registration.")
            continue
        print("--------------------------------")
        print("Register input:")
        print(f"dex: {dex_name}")
        print(f"coin: {f'{dex_name}:{market_name}'}")
        print(f"sz_decimals: {market['szDecimals']}")
        print(f"oracle_px: {oracle_pxs[market_name]}")
        print(f"margin_table_id: {market['marginTableId']}")
        print(f"only_isolated: {False}")
        print(f"schema: {schema}")

        register_asset_result = exchange.perp_deploy_register_asset(
            dex=dex_name,
            max_gas=1000000000000,  # Example gas, might need adjustment
            coin=f"{dex_name}:{market_name}",
            sz_decimals=market["szDecimals"],
            oracle_px=oracle_pxs[market_name],
            margin_table_id=market["marginTableId"],
            only_isolated=False,
            schema=schema,
        )
        print(f"Register asset {market_name} result:", register_asset_result)

        if "error" in register_asset_result.get("response", {}):
            print(f"Error registering {market_name}: {register_asset_result['response']['error']}")

    # get the new dex meta
    print(f"Meta for {dex_name}:", info.meta(dex=dex_name))


if __name__ == "__main__":
    main()
