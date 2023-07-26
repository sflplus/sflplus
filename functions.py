import streamlit as st
from pandas import DataFrame, Series
import pandas as pd
import requests
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from main import Main


@st.cache_resource(
    ttl=3600, show_spinner="Updating the NFTs Prices"
)  # cache for 1 hour
def nft_price_read() -> list[DataFrame] | None:
    url = (
        "https://docs.google.com/spreadsheets/u/1/d/e/"
        + "2PACX-1vQmTGM6vgASegLvLcNPSgAlVsMkm9mBx-PBRs-"
        + "nKUc3MkGiYxwwl7yKltWciQ_x2Q/pubhtml"
    )
    dfs: list[DataFrame] = pd.read_html(url)
    return dfs


@st.cache_resource(ttl=300, show_spinner="Updating the NFT Prices")
def nft_price(
    _main: "Main", item_name=None, return_type="result_df"
) -> DataFrame | None:
    dfs: list[DataFrame] | None = nft_price_read()
    if dfs is None:
        return
    df: DataFrame = pd.concat(dfs, axis=0)
    # drop the first columns
    df.drop(df.columns[[0]], axis=1, inplace=True)

    # rename the remaining columns
    df.rename(
        columns={"Unnamed: 2": "Last Sale", "Unnamed: 3": "Current Price"},
        inplace=True,
    )
    df.rename(columns={df.columns[0]: "NFT"}, inplace=True)

    # create a list of names to exclude
    exclude_names: list[str] = [
        "Purple Egg",
        "Red Egg",
        "Blue Egg",
        "Yellow Egg",
        "Orange Egg",
        "Pink Egg",
        "Green Egg",
        "Egg Basket",
        "Angel Bear",
        "Sunflower",
        "Potato",
        "Pumpkin",
        "Carrot",
        "Cabbage",
        "Beetroot",
        "Cauliflower",
        "Parsnip",
        "Radish",
        "Wheat",
        "Kale",
        "Apple",
        "Orange",
        "Blueberry",
        "Wood",
        "Stone",
        "Iron",
        "Gold",
        "Egg",
        "Iron Pickaxe",
        "Stone Pickaxe",
        "Pickaxe",
        "Axe",
        "Eggplant",
        "Chicken",
        "Wild Mushroom",
        "Chef Apron",
    ]
    # create a boolean mask for the rows that contain any of the
    # excluded names in the 'NFT' column
    name_mask: Series[bool] = df["NFT"].isin(exclude_names)

    # create a boolean mask for the rows that contain 'Flag' as
    # part of their name in the 'NFT' column
    flag_mask: Series[bool] = df["NFT"].str.contains("Flag")

    # create a boolean mask that selects only the rows that do
    # not contain any of the excluded names and also do not contain
    # 'Flag' as part of their name
    mask: Series[bool] = ~(name_mask | flag_mask)

    # select the rows that do not contain any of the excluded names and
    # also do not contain 'Flag' as part of their name
    df = df[mask]

    # clean the "Last Sale" values
    df["Last Sale"] = df["Last Sale"].str.replace("Last sale: ", "")
    for index, value in df["Last Sale"].items():
        if "<" in value or ">" in value:
            df.at[index, "Last Sale"] = None

    # convert prices in Matic and ETH to USD
    for i, row in df.iterrows():
        last_sale = row["Last Sale"]
        if isinstance(last_sale, str) and last_sale.endswith("K MATIC"):
            price_str = last_sale.replace("K MATIC", "")
            price_float = float(price_str.replace(",", ""))
            last_sale_usd = price_float * _main.matic_price * 1000
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith("MATIC"):
            last_sale_usd: float = (
                float(last_sale.split()[0].replace(",", "")) * _main.matic_price
            )
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith("ETH"):
            last_sale_usd = (
                float(last_sale.split()[0].replace(",", "")) * _main.eth_price
            )
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith("K USDC"):
            price_str: str = last_sale.replace("K USDC", "")
            price_float = float(price_str.replace(",", ""))
            last_sale_usd = int(price_float * 1000)
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"

        current_price = row["Current Price"]
        if isinstance(current_price, str) and current_price.endswith("K MATIC"):
            price_str = current_price.replace("K MATIC", "")
            price_float = float(price_str.replace(",", ""))
            current_price_usd: float = price_float * _main.matic_price * 1000
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith("MATIC"):
            matic_price_usd = float(_main.matic_price)
            current_price_usd: float = (
                float(current_price.split()[0].replace(",", ""))
                * matic_price_usd
            )
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith("ETH"):
            eth_price_usd = float(_main.eth_price)
            current_price_usd = (
                float(current_price.split()[0].replace(",", "")) * eth_price_usd
            )
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith(
            "K USDC"
        ):
            price_str = current_price.replace("K USDC", "")
            price_float = float(price_str.replace(",", ""))
            current_price_usd = int(price_float * 1000)
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"

    # Clean the Last Sale and Current price to leave only numbers
    df["Last Sale"] = df["Last Sale"].astype(str).str.replace(",", "")
    df["Current Price"] = df["Current Price"].astype(str).str.replace(",", "")

    df["Last Sale"] = df["Last Sale"].str.extract(r"([\d.]+)").astype(float)
    df["Current Price"] = (
        df["Current Price"].str.extract(r"([\d.]+)").astype(float)
    )

    df.dropna(subset=["Last Sale", "Current Price"], how="all", inplace=True)

    # calculate the average price for each NFT
    df["Average Price"] = df[["Last Sale", "Current Price"]].apply(
        lambda x: x.sum() / 2
        if (not pd.isnull(x["Last Sale"]))
        and (not pd.isnull(x["Current Price"]))
        else x.max(),
        axis=1,
    )

    # round the average price to 2 decimals
    df["Average Price"] = df["Average Price"].round(2)

    # create a new DataFrame with only the "NFT" and "Average Price" columns
    df = df[["NFT", "Average Price"]]

    # Return the result based on the specified 'return_type'
    if return_type == "nft_list":
        if item_name is not None and item_name in df["NFT"].values:
            current_price: Any = df.loc[df["NFT"] == item_name, "Average Price"]
            return current_price.values[0]
        else:
            return None
    else:
        return df


def nft_buffs(main, inventory, return_type="result_df"):
    df: DataFrame | None = nft_price(main, return_type=return_type)
    if df is None:
        df = pd.DataFrame()
    result_df = pd.concat([df], axis=0)

    # Check if the items in the 'NFT' column are present in the
    # keys of the 'inventory' dictionary
    result_df.loc[result_df["NFT"].isin(inventory.keys()), "Quantity"] = True

    # Replace 'True' with the corresponding values from the
    # 'inventory' dictionary
    result_df.loc[
        result_df["NFT"].isin(inventory.keys()), "Quantity"
    ] = result_df.loc[result_df["NFT"].isin(inventory.keys()), "NFT"].map(
        inventory
    )

    # Drop rows where 'Quantity' is NaN
    result_df = result_df.dropna(subset=["Quantity"])

    # Convert 'Quantity' to integers
    result_df[
        result_df.columns[result_df.columns.get_loc("Quantity")]
    ] = result_df["Quantity"].astype(int)

    # Calculate the total price and drop the 'Average Price' column
    result_df.loc[:, "Total Price"] = (
        result_df["Quantity"] * result_df["Average Price"]
    )
    result_df.drop(columns=["Average Price"], inplace=True)
    result_df = result_df.sort_values(by="Total Price", ascending=False)
    result_df["Total Price"] = result_df["Total Price"].apply(
        lambda x: f"${x:.2f}"
    )
    # Calculate the total value of NFT buffs
    # total_value_nft_buffs = result_df['Total Price'].
    # str.replace('$', '', regex=False).astype(float).sum()
    total_value_nft_buffs: float = (
        result_df["Total Price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .astype(float)
        .sum()
    )

    # Set the 'NFT' column as the index of the dataframe
    result_df: DataFrame = result_df.set_index("NFT")

    # Return the result based on the specified 'return_type'
    if return_type == "total":
        return total_value_nft_buffs
    else:
        return result_df


@st.cache_resource(
    ttl=3600, show_spinner="Updating the Wearables Prices"
)  # cache for 1 hour
def wearable_price_read() -> list[DataFrame]:
    url = (
        "https://docs.google.com/spreadsheets/d/e/"
        + "2PACX-1vRcGDBOuVgP9v-sklfUIy40DMVO3IfLId62cokp0ABYeNEWQZkVZ"
        + "f3qLHweSR4DXQ/pubhtml"
    )
    dfs: list[DataFrame] = pd.read_html(url)
    return dfs


@st.cache_resource(ttl=300, show_spinner="Updating the Wearables Prices")
def wearable_price(_main: "Main", item_name=None, return_type="result_df"):
    dfs: list[DataFrame] = wearable_price_read()
    df: DataFrame = pd.concat(dfs, axis=0)
    # drop the first columns
    df.drop(df.columns[[0]], axis=1, inplace=True)

    # rename the remaining columns
    df.rename(
        columns={"Unnamed: 2": "Last Sale", "Unnamed: 3": "Current Price"},
        inplace=True,
    )
    df.rename(columns={df.columns[0]: "Wearable"}, inplace=True)

    # create a list of names to exclude
    # exclude_names = ['Beach Sarong','Dawn Lamp','Developer Hoodie',
    # 'Lifeguard Hat','Lifeguard Pants',
    # 'Lifeguard Shirt','Polkastarter Shirt','Sequence Hat','Sequence Shirt',
    # 'Sunburst Potion','Tropical Sarong']
    # name_mask = df['Wearable'].isin(exclude_names)
    # mask = ~(name_mask)
    # df = df[mask]

    # clean the "Last Sale" values
    df["Last Sale"] = df["Last Sale"].str.replace("Last sale: ", "")
    for index, value in df["Last Sale"].items():
        if isinstance(value, str) and ("<" in value or ">" in value):
            df.at[index, "Last Sale"] = None

    # convert prices in Matic and ETH to USD
    for i, row in df.iterrows():
        last_sale = row["Last Sale"]
        if isinstance(last_sale, str) and last_sale.endswith("K MATIC"):
            price_str = last_sale.replace("K MATIC", "")
            price_float = float(price_str.replace(",", ""))
            matic_price_usd = float(_main.matic_price)
            last_sale_usd = price_float * matic_price_usd * 1000
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith("MATIC"):
            matic_price_usd = float(_main.matic_price)
            last_sale_usd = (
                float(last_sale.split()[0].replace(",", "")) * matic_price_usd
            )
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith("ETH"):
            eth_price_usd = float(_main.eth_price)
            last_sale_usd: float = (
                float(last_sale.split()[0].replace(",", "")) * eth_price_usd
            )
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith("K USDC"):
            price_str: str = last_sale.replace("K USDC", "")
            price_float = float(price_str.replace(",", ""))
            last_sale_usd = int(price_float * 1000)
            df.at[i, "Last Sale"] = f"{last_sale_usd:.2f} USDC"

        current_price = row["Current Price"]
        if isinstance(current_price, str) and current_price.endswith("K MATIC"):
            price_str = current_price.replace("K MATIC", "")
            price_float = float(price_str.replace(",", ""))
            matic_price_usd = float(_main.matic_price)
            current_price_usd: float = price_float * matic_price_usd * 1000
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith("MATIC"):
            matic_price_usd = float(_main.matic_price)
            current_price_usd = (
                float(current_price.split()[0].replace(",", ""))
                * matic_price_usd
            )
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith("ETH"):
            eth_price_usd = float(_main.eth_price)
            current_price_usd = (
                float(current_price.split()[0].replace(",", "")) * eth_price_usd
            )
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith(
            "K USDC"
        ):
            price_str = current_price.replace("K USDC", "")
            price_float = float(price_str.replace(",", ""))
            current_price_usd = int(price_float * 1000)
            df.at[i, "Current Price"] = f"{current_price_usd:.2f} USDC"

    # Clean the Last Sale and Current price to leave only numbers
    df["Last Sale"] = df["Last Sale"].astype(str).str.replace(",", "")
    df["Current Price"] = df["Current Price"].astype(str).str.replace(",", "")

    df["Last Sale"] = df["Last Sale"].str.extract(r"([\d.]+)").astype(float)
    df["Current Price"] = (
        df["Current Price"].str.extract(r"([\d.]+)").astype(float)
    )

    df.dropna(subset=["Last Sale", "Current Price"], how="all", inplace=True)

    # calculate the average price for each NFT
    # df['Average Price'] = df[['Last Sale', 'Current Price']].
    # apply(lambda x: x.sum() / 2 if (not pd.isnull(x['Last Sale'])) and
    # (not pd.isnull(x['Current Price'])) else x.max(), axis=1)

    # round the average price to 2 decimals
    # df['Average Price'] = df['Average Price'].round(2)

    df.rename(columns={"Last Sale": "Average Price"}, inplace=True)

    # create a new DataFrame with only the "NFT" and "Average Price" columns
    df = df[["Wearable", "Average Price"]]

    # Return the result based on the specified 'return_type'
    if return_type == "nft_list":
        if item_name is not None and item_name in df["Wearable"].values:
            current_price: Any = df.loc[
                df["Wearable"] == item_name, "Average Price"
            ]
            return current_price.values[0]
        else:
            return None
    else:
        return df


@st.cache_resource(ttl=604800, show_spinner="Updating Lantern Ingredients")
def retrieve_lantern_ingredients() -> tuple[Any, None] | tuple[Any, Any]:
    url = "https://api.sunflower-land.com/visit/1"
    response: requests.Response = requests.get(url)

    if response.status_code == 200:
        data: dict[str, dict] = response.json()
        state: dict[str, dict] = data.get("state", {})
        dawnBreaker: dict[str, Any] = state.get("dawnBreaker", {})
        current_lanterns: Any = dawnBreaker.get("availableLantern")
        lanterns_ing: Any = current_lanterns.get("ingredients")
        lanterns_sfl: Any = current_lanterns.get("sfl")

        if lanterns_sfl is None:
            return lanterns_ing, None
        else:
            lanterns_sfl = float(lanterns_sfl)
            return lanterns_ing, lanterns_sfl
    else:
        raise Exception(
            f"Failed to retrieve lantern ingredients. "
            + f"Error: {response.status_code}"
        )


@st.cache_resource(
    ttl=1800, show_spinner="Updating the NFT Minted"
)  # cache for 30 MIN
def fetch_owner_count(query_id, api_key: str) -> int | None:
    dune_api_url: str = (
        f"https://api.dune.com/api/v1/query/"
        + f"{query_id}/results?api_key={api_key}"
    )
    response: requests.Response = requests.get(dune_api_url)

    if response.status_code == 200:
        data: dict = response.json()
        owner_count: int = data["result"]["rows"][0]["_col0"]
        return owner_count
    else:
        raise Exception()
        live_minted_error.error(
            f"Error fetching NFT owners"
        )  # for query {query_id}


def wearable_list(
    _main: "Main", equipped_dict: dict, return_type="filtered_df"
):
    df: DataFrame | None = wearable_price(_main, return_type=return_type)
    if df is None:
        df = pd.DataFrame()
    wearables = list(equipped_dict.values())

    filtered_df: DataFrame = df[df["Wearable"].isin(wearables)].copy()
    filtered_df["Wearable"] = filtered_df["Wearable"].replace(equipped_dict)
    filtered_df.reset_index(drop=True, inplace=True)

    for wearable in wearables:
        if wearable in _main.wearables_sfl:
            filtered_df.loc[
                filtered_df["Wearable"] == wearable, "Average Price"
            ] = (_main.wearables_sfl[wearable] * _main.sfl_price)

    filtered_df = filtered_df.sort_values(by="Average Price", ascending=False)
    filtered_df["Average Price"] = filtered_df["Average Price"].apply(
        lambda x: f"${x:.2f}"
    )

    total_value_wearable = (
        filtered_df["Average Price"]
        .str.replace("$", "", regex=False)
        .astype(float)
        .sum()
    )
    filtered_df.rename(columns={"Average Price": "Last Sale"}, inplace=True)
    filtered_df = filtered_df.set_index("Wearable")

    if return_type == "total":
        return total_value_wearable
    else:
        return filtered_df
