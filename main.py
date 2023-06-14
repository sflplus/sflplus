import streamlit as st
from streamlit import components
import json
import requests
import time
from PIL import Image
from decimal import Decimal
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from streamlit_tags import st_tags
import pandas as pd
import urllib.request
import asyncio
import aiohttp
from datetime import datetime, timedelta
import sys
import fuzzywuzzy.fuzz as fuzz

favicon = Image.open('favicon.png')

st.set_page_config(
    page_title="SFL Plus",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

st.write(
    '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")


@st.cache_resource(ttl=604800, show_spinner="Updating Lantern Ingredients")
def retrieve_lantern_ingredients():
    url = "https://api.sunflower-land.com/visit/1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        state = data.get("state")
        dawnBreaker = state.get("dawnBreaker")
        current_lanterns = dawnBreaker.get("availableLantern")
        lanterns_ing = current_lanterns.get("ingredients")
        lanterns_sfl = current_lanterns.get("sfl")

        if lanterns_sfl is None:
            return lanterns_ing, None
        else:
            lanterns_sfl = float(lanterns_sfl)
            return lanterns_ing, lanterns_sfl
    else:
        raise Exception(f"Failed to retrieve lantern ingredients. Error: {response.status_code}")


@st.cache_resource(ttl=600, show_spinner="Updating the Resouces Prices") # cache for 10 min
def get_resource_price(resource_id):
    url = f'https://sfl.tools/api/listings?resourceId={resource_id}&page=1&pageSize=1&sortColumn=pricePerUnit&sortDirection=asc'
    response2 = requests.get(url).json()
    if len(response2) > 0:
        price = response2[0]['calculations']['pricePerUnit']
        return Decimal(price) / Decimal(10**18)
    else:
        raise Exception("Failed to get resouces prices.")

@st.cache_resource(ttl=3600, show_spinner="Updating the SFL Supply") # cache for 1 hour
def get_token_supply():
    try:
        url = f'https://api.polygonscan.com/api?module=stats&action=tokensupply&contractaddress=0xd1f9c58e33933a993a3891f8acfe05a68e1afc05&apikey=QJKGEWQQI8UQSZQDMQQPYJU8Q7D5CCDSQV'
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to get SFL Supply.")  
        supply = response.json()['result']
        return int(supply)
    except:
        return None

def get_eth_price():
    url = 'https://api.dexscreener.com/latest/dex/pairs/bsc/0x63b30de1a998e9e64fd58a21f68d323b9bcd8f85'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to get ETH price from Dexscreener API.")
    eth_price = response.json()['pairs'][0]['priceUsd']
    return eth_price    
    
def get_eth_price2():
    eth_url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
    eth_response = requests.get(eth_url)
    if eth_response.status_code != 200:
        raise Exception("Failed to get Ethereum price from Coingecko API.")
    eth_price = eth_response.json()['ethereum']['usd']
    return eth_price

def get_matic_price():
    url = 'https://api.dexscreener.com/latest/dex/pairs/ethereum/0x290a6a7460b308ee3f19023d2d00de604bcf5b42'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to get ETH price from Dexscreener API.")
    matic_price = response.json()['pairs'][0]['priceUsd']
    return matic_price

def get_matic_price2():
    matic_url = 'https://api.coingecko.com/api/v3/simple/price?ids=matic-network&vs_currencies=usd'
    matic_response = requests.get(matic_url)
    if matic_response.status_code != 200:
        raise Exception("Failed to get Matic price from Coingecko API.")
    matic_price = matic_response.json()['matic-network']['usd']
    return matic_price

def get_sfl_price():
    url = 'https://api.dexscreener.com/latest/dex/pairs/polygon/0x6f9E92DD4734c168A734B873dC3db77E39552eb6'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to get SFL price from Dexscreener API.")
    sfl_price = response.json()['pairs'][0]['priceUsd']
    return sfl_price

def get_sfl_price2():
    sfl_url = 'https://api.coingecko.com/api/v3/simple/price?ids=sunflower-land&vs_currencies=usd'
    sfl_response = requests.get(sfl_url)
    if sfl_response.status_code != 200:
        raise Exception("Failed to get SFL price from Coingecko API.")
    sfl_price = sfl_response.json()['sunflower-land']['usd']
    return sfl_price

@st.cache_resource(ttl=3600, show_spinner="Updating the ETH Price") # cache for 1 hour
def retrieve_eth_price():
    eth_price = get_eth_price()
    if eth_price is None:
        eth_price = get_eth_price2()
        if eth_price is None:
            raise Exception("Failed to retrieve Ethereum price from both Coingecko and Dexscreener APIs. Please try again later.")
    return eth_price

@st.cache_resource(ttl=3600, show_spinner="Updating the Matic Price") # cache for 1 hour
def retrieve_matic_price():
    matic_price = get_matic_price()
    if matic_price is None:
        matic_price = get_matic_price2()
        if matic_price is None:
            raise Exception("Failed to retrieve Matic price from both Coingecko and Dexscreener APIs. Please try again later.")
    return matic_price

@st.cache_resource(ttl=3600, show_spinner="Updating the SFL Price") # cache for 1 hour
def retrieve_sfl_price():
    sfl_price = get_sfl_price()
    if sfl_price is None:
        sfl_price = get_sfl_price2()
        if sfl_price is None:
            raise Exception("Failed to retrieve SFL price from both Coingecko and Dexscreener APIs. Please try again later.")
    return sfl_price


eth_price_float = retrieve_eth_price()
matic_price_float = retrieve_matic_price()
sfl_price_float = retrieve_sfl_price()

sfl_price = float(sfl_price_float)
matic_price = float(matic_price_float)
eth_price = float(eth_price_float)

sfl_supply = get_token_supply()

API_KEY_DUNE = "xEB9BjuGBc5SbpVABb2VHcVV5DQ1g3K2"

queries = ["2427513", "2427509", "2427499"]
queries_name = ["Maximus", "Obie", "Purple Trail"]
queries_quantity = ["350", "2500", "10000"]
queries_emoji = ["💜", "🍆", "🐌"]
queries_ticket = ["3200", "1200", "500"]

#@st.cache_resource(ttl=1800, show_spinner="Updating the NFT Minted") # cache for 30 MIN
def fetch_owner_count(query_id):
    dune_api_url = f"https://api.dune.com/api/v1/query/{query_id}/results?api_key={API_KEY_DUNE}"
    response = requests.get(dune_api_url)
    
    if response.status_code == 200:
        data = response.json()
        owner_count = data["result"]["rows"][0]["_col0"]
        return owner_count
    else:
        live_minted_error.error(f"Error fetching NFT owners") #for query {query_id}

@st.cache_resource(ttl=7200, show_spinner="Updating Top10 ID") # cache for 2 hour
def fetch_top_ten_ids():
    try:
        # Sending the request to the second API
        response = requests.get("https://api.sunflower-land.com/leaderboard/lanterns/1").json()
        top_ten_ids = [entry["id"] for entry in response["topTen"]]
        return top_ten_ids
    except Exception as e:
        print(f"Failed to fetch top ten IDs. Error: {e}")
        return []

@st.cache_resource(ttl=780, show_spinner="Updating Top10 lanterns") # cache for 13 min
def retrieve_lanterns_data(top_ten_ids):
    # Building payload using the provided IDs
    payload = json.dumps({"ids": top_ten_ids})
    headers = {'Content-Type': 'application/json'}

    # Sending the request to the first API
    response = requests.post("https://api.sunflower-land.com/community/getFarms", headers=headers, data=payload).json()

    # Processing the response from the first API
    skipped_farms = response['skipped']
    farms = response['farms']

    lanterns_data = {}
    for farm_id, farm in farms.items():
        try:
            farm_data = farm.get('dawnBreaker', {}).get('lanternsCraftedByWeek', {})
            week_data = {
                str(week): farm_data.get(str(week), 0)
                for week in range(1, 7)
            }
            lanterns_data[str(farm_id)] = week_data
        except Exception as e:
            pass

    return lanterns_data

@st.cache_resource(ttl=3600, show_spinner="Updating the NFTs Prices") # cache for 1 hour
def nft_price_read():
    url = 'https://docs.google.com/spreadsheets/u/1/d/e/2PACX-1vQmTGM6vgASegLvLcNPSgAlVsMkm9mBx-PBRs-nKUc3MkGiYxwwl7yKltWciQ_x2Q/pubhtml'
    try:
        dfs = pd.read_html(url)
    except Exception as e:
        #farm_worth_nft.error("Error reading the Opensea Prices", e)
        pass
    return dfs

@st.cache_resource(ttl=300, show_spinner="Updating the NFT Prices")
def nft_price(item_name=None, return_type='result_df'):
    dfs = nft_price_read()
    df = pd.concat(dfs, axis=0)
    # drop the first columns
    df.drop(df.columns[[0]], axis=1, inplace=True)

    # rename the remaining columns
    df.rename(columns={'Unnamed: 2': 'Last Sale', 'Unnamed: 3': 'Current Price'}, inplace=True)
    df.rename(columns={df.columns[0]: 'NFT'}, inplace=True)
    
    # create a list of names to exclude
    exclude_names = ['Purple Egg', 'Red Egg', 'Blue Egg', 'Yellow Egg', 'Orange Egg', 
                     'Pink Egg', 'Green Egg', 'Egg Basket', 'Angel Bear', 'Sunflower',
                     'Potato', 'Pumpkin', 'Carrot', 'Cabbage', 'Beetroot', 'Cauliflower',
                     'Parsnip', 'Radish', 'Wheat', 'Kale', 'Apple', 'Orange', 'Blueberry',
                     'Wood', 'Stone', 'Iron', 'Gold', 'Egg', 'Iron Pickaxe', 'Stone Pickaxe',
                     'Pickaxe', 'Axe', 'Eggplant', 'Chicken', 'Wild Mushroom', 'Chef Apron']
    # create a boolean mask for the rows that contain any of the excluded names in the 'NFT' column
    name_mask = df['NFT'].isin(exclude_names)
    # create a boolean mask for the rows that contain 'Flag' as part of their name in the 'NFT' column
    flag_mask = df['NFT'].str.contains('Flag')
    # create a boolean mask that selects only the rows that do not contain any of the excluded names and also do not contain 'Flag' as part of their name
    mask = ~(name_mask | flag_mask)
    # select the rows that do not contain any of the excluded names and also do not contain 'Flag' as part of their name
    df = df[mask]    

    # clean the "Last Sale" values
    df['Last Sale'] = df['Last Sale'].str.replace('Last sale: ', '').str.replace('<', '')

    # convert prices in Matic and ETH to USD
    for i, row in df.iterrows():
        last_sale = row['Last Sale']
        if isinstance(last_sale, str) and last_sale.endswith('K MATIC'):
            price_str = last_sale.replace('K MATIC', '')
            price_float = float(price_str.replace(',', ''))
            last_sale_usd = price_float * matic_price_usd * 1000
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith('MATIC'):
            matic_price_usd = float(matic_price)
            last_sale_usd = float(last_sale.split()[0].replace(',', '')) * matic_price_usd
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith('ETH'):
            eth_price_usd = float(eth_price)
            last_sale_usd = float(last_sale.split()[0].replace(',', '')) * eth_price_usd
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith('K USDC'):
            price_str = last_sale.replace('K USDC', '')
            price_float = float(price_str.replace(',', ''))
            last_sale_usd = int(price_float * 1000)
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"

        current_price = row['Current Price']
        if isinstance(current_price, str) and current_price.endswith('K MATIC'):
            price_str = current_price.replace('K MATIC', '')
            price_float = float(price_str.replace(',', ''))
            current_price_usd = price_float * matic_price_usd * 1000
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith('MATIC'):
            matic_price_usd = float(matic_price)
            current_price_usd = float(current_price.split()[0].replace(',', '')) * matic_price_usd
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith('ETH'):
            eth_price_usd = float(eth_price)
            current_price_usd = float(current_price.split()[0].replace(',', '')) * eth_price_usd
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith('K USDC'):
            price_str = current_price.replace('K USDC', '')
            price_float = float(price_str.replace(',', ''))
            current_price_usd = int(price_float * 1000)
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"


    # Clean the Last Sale and Current price to leave only numbers
    df['Last Sale'] = df['Last Sale'].astype(str).str.replace(',', '')
    df['Current Price'] = df['Current Price'].astype(str).str.replace(',', '')

    df['Last Sale'] = df['Last Sale'].str.extract(r'([\d.]+)').astype(float)
    df['Current Price'] = df['Current Price'].str.extract(r'([\d.]+)').astype(float)

    df.dropna(subset=['Last Sale', 'Current Price'], how='all', inplace=True)

    # calculate the average price for each NFT
    df['Average Price'] = df[['Last Sale', 'Current Price']].apply(lambda x: x.sum() / 2 if (not pd.isnull(x['Last Sale'])) and (not pd.isnull(x['Current Price'])) else x.max(), axis=1)

    # round the average price to 2 decimals
    df['Average Price'] = df['Average Price'].round(2)

    # create a new DataFrame with only the "NFT" and "Average Price" columns
    df = df[['NFT', 'Average Price']]
    
    # Return the result based on the specified 'return_type'
    if return_type == 'nft_list':
        if item_name is not None and item_name in df['NFT'].values:
            current_price = df.loc[df['NFT'] == item_name, 'Average Price'].values[0]
            return current_price
        else:
            return None
    else:
        return df
   
def nft_buffs(inventory, return_type='result_df'):
    df = nft_price(return_type=return_type)
    result_df = pd.concat([df], axis=0)

    # Check if the items in the 'NFT' column are present in the keys of the 'inventory' dictionary
    result_df.loc[result_df['NFT'].isin(inventory.keys()), 'Quantity'] = True

    # Replace 'True' with the corresponding values from the 'inventory' dictionary
    result_df.loc[result_df['NFT'].isin(inventory.keys()), 'Quantity'] = result_df.loc[result_df['NFT'].isin(inventory.keys()), 'NFT'].map(inventory)

    # Drop rows where 'Quantity' is NaN
    result_df = result_df.dropna(subset=['Quantity'])
    

    # Convert 'Quantity' to integers
    result_df[result_df.columns[result_df.columns.get_loc('Quantity')]] = result_df['Quantity'].astype(int)

    # Calculate the total price and drop the 'Average Price' column
    result_df.loc[:, 'Total Price'] = result_df['Quantity'] * result_df['Average Price']
    result_df.drop(columns=['Average Price'], inplace=True)
    result_df = result_df.sort_values(by='Total Price', ascending=False)     
    result_df['Total Price'] = result_df['Total Price'].apply(lambda x: f'${x:.2f}')   
    # Calculate the total value of NFT buffs
    #total_value_nft_buffs = result_df['Total Price'].str.replace('$', '', regex=False).astype(float).sum()
    total_value_nft_buffs = result_df['Total Price'].astype(str).str.replace('$', '', regex=False).astype(float).sum()

    
    # Set the 'NFT' column as the index of the dataframe
    result_df = result_df.set_index('NFT')

    # Return the result based on the specified 'return_type'
    if return_type == 'total':
        return total_value_nft_buffs
    else:
        return result_df    
    
@st.cache_resource(ttl=3600, show_spinner="Updating the Wearables Prices") # cache for 1 hour
def wearable_price_read():
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRcGDBOuVgP9v-sklfUIy40DMVO3IfLId62cokp0ABYeNEWQZkVZf3qLHweSR4DXQ/pubhtml'
    try:
        dfs = pd.read_html(url)
    except Exception as e:
        #farm_worth_nft.error("Error reading the Opensea Prices", e)
        pass
    return dfs

@st.cache_resource(ttl=300, show_spinner="Updating the Wearables Prices")
def wearable_price(item_name=None, return_type='result_df'):
    dfs = wearable_price_read()
    df = pd.concat(dfs, axis=0)
    # drop the first columns
    df.drop(df.columns[[0]], axis=1, inplace=True)

    # rename the remaining columns
    df.rename(columns={'Unnamed: 2': 'Last Sale', 'Unnamed: 3': 'Current Price'}, inplace=True)
    df.rename(columns={df.columns[0]: 'Wearable'}, inplace=True)
    
    # create a list of names to exclude
    #exclude_names = ['Beach Sarong','Dawn Lamp','Developer Hoodie','Lifeguard Hat','Lifeguard Pants',
    #'Lifeguard Shirt','Polkastarter Shirt','Sequence Hat','Sequence Shirt','Sunburst Potion','Tropical Sarong']
    #name_mask = df['Wearable'].isin(exclude_names)
    #mask = ~(name_mask)
    #df = df[mask]    

    # clean the "Last Sale" values
    df['Last Sale'] = df['Last Sale'].str.replace('Last sale: ', '').str.replace('<', '')

    # convert prices in Matic and ETH to USD
    for i, row in df.iterrows():
        last_sale = row['Last Sale']
        if isinstance(last_sale, str) and last_sale.endswith('K MATIC'):
            price_str = last_sale.replace('K MATIC', '')
            price_float = float(price_str.replace(',', ''))
            last_sale_usd = price_float * matic_price_usd * 1000
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith('MATIC'):
            matic_price_usd = float(matic_price)
            last_sale_usd = float(last_sale.split()[0].replace(',', '')) * matic_price_usd
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith('ETH'):
            eth_price_usd = float(eth_price)
            last_sale_usd = float(last_sale.split()[0].replace(',', '')) * eth_price_usd
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"
        elif isinstance(last_sale, str) and last_sale.endswith('K USDC'):
            price_str = last_sale.replace('K USDC', '')
            price_float = float(price_str.replace(',', ''))
            last_sale_usd = int(price_float * 1000)
            df.at[i, 'Last Sale'] = f"{last_sale_usd:.2f} USDC"

        current_price = row['Current Price']
        if isinstance(current_price, str) and current_price.endswith('K MATIC'):
            price_str = current_price.replace('K MATIC', '')
            price_float = float(price_str.replace(',', ''))
            current_price_usd = price_float * matic_price_usd * 1000
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith('MATIC'):
            matic_price_usd = float(matic_price)
            current_price_usd = float(current_price.split()[0].replace(',', '')) * matic_price_usd
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith('ETH'):
            eth_price_usd = float(eth_price)
            current_price_usd = float(current_price.split()[0].replace(',', '')) * eth_price_usd
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"
        elif isinstance(current_price, str) and current_price.endswith('K USDC'):
            price_str = current_price.replace('K USDC', '')
            price_float = float(price_str.replace(',', ''))
            current_price_usd = int(price_float * 1000)
            df.at[i, 'Current Price'] = f"{current_price_usd:.2f} USDC"


    # Clean the Last Sale and Current price to leave only numbers
    df['Last Sale'] = df['Last Sale'].astype(str).str.replace(',', '')
    df['Current Price'] = df['Current Price'].astype(str).str.replace(',', '')

    df['Last Sale'] = df['Last Sale'].str.extract(r'([\d.]+)').astype(float)
    df['Current Price'] = df['Current Price'].str.extract(r'([\d.]+)').astype(float)

    df.dropna(subset=['Last Sale', 'Current Price'], how='all', inplace=True)

    # calculate the average price for each NFT
    #df['Average Price'] = df[['Last Sale', 'Current Price']].apply(lambda x: x.sum() / 2 if (not pd.isnull(x['Last Sale'])) and (not pd.isnull(x['Current Price'])) else x.max(), axis=1)

    # round the average price to 2 decimals
    #df['Average Price'] = df['Average Price'].round(2)

    df.rename(columns={'Last Sale': 'Average Price'}, inplace=True)
    
    # create a new DataFrame with only the "NFT" and "Average Price" columns
    df = df[['Wearable', 'Average Price']]
    
    # Return the result based on the specified 'return_type'
    if return_type == 'nft_list':
        if item_name is not None and item_name in df['Wearable'].values:
            current_price = df.loc[df['Wearable'] == item_name, 'Average Price'].values[0]
            return current_price
        else:
            return None
    else:
        return df
    
def wearable_list(equipped_dict, return_type='filtered_df'):
    df = wearable_price(return_type=return_type)
    wearables = list(equipped_dict.values())

    filtered_df = df[df['Wearable'].isin(wearables)].copy()
    filtered_df['Wearable'] = filtered_df['Wearable'].replace(equipped_dict)
    filtered_df.reset_index(drop=True, inplace=True)

    for wearable in wearables:
        if wearable in wearables_sfl:
            filtered_df.loc[filtered_df['Wearable'] == wearable, 'Average Price'] = wearables_sfl[wearable] * sfl_price

    filtered_df = filtered_df.sort_values(by='Average Price', ascending=False)
    filtered_df['Average Price'] = filtered_df['Average Price'].apply(lambda x: f'${x:.2f}')

    total_value_wearable = filtered_df['Average Price'].str.replace('$', '', regex=False).astype(float).sum()
    filtered_df.rename(columns={'Average Price': 'Last Sale'}, inplace=True)
    filtered_df = filtered_df.set_index('Wearable')

    if return_type == 'total':
        return total_value_wearable
    else:
        return filtered_df

app_state = st.experimental_get_query_params()
app_state = {k: v[0] if isinstance(v, list) else v for k, v in app_state.items()} # fetch the first item in each query string as we don't have multiple values for each query string key in this example




col00, col11x, col0x, col10x = st.columns([1.85,1.75,1.75,3.5])
with col00:
    st.markdown('[![Foo](https://raw.githubusercontent.com/vitt0/sunflower-land/main/sflplus.png)](https://sflplus.info)  <span style="vertical-align:bottom;color:rgb(0, 221, 66);font-weight:bold;">v3.2</span>', unsafe_allow_html=True)
with col11x:
    general_info = st.container()
    if sfl_supply is not None:
        format_supply = "{:,.0f}".format(sfl_supply / 1e18)
        supply_progress = 10000000 - (float(format_supply.replace(',', '')) - 20000000)
    else:
        general_info.error("Failed to get SFL Supply. Please try again later.")
        format_supply = "N/A"
        supply_progress = 0
with col0x:
    general_info2 = st.container()

with col10x:
    general_info3 = st.container()

    supply_progress_per = (supply_progress / 10000000) * 100
    supply_percentage_float = float(supply_progress_per)
    supply_percentage_number = "{:.2f}".format(supply_percentage_float)
    supply_progress_percentage = 100 - float(supply_percentage_number)
    supply_percentage_final = float(supply_percentage_number) / 100
    supply_percentage_inv =  1 - supply_percentage_final 

    general_info.write(f" 🟣 Matic: **{matic_price:.2f}** - 🌻 SFL: **{sfl_price:.4f}**")
    general_info.write(f" 📈 Current Supply: **{format_supply}**")
    general_info2.write(f" ⏳ Next Halvening: **30,000,000**")
    general_info2.write(f" 📊 In Percentage: **{supply_progress_percentage:.2f}%**")
    #general_info.progress(supply_percentage_inv, text=None)
    #features_info = st.expander("📗 **FEATURES**", expanded=False)

st.divider()
general_info3.markdown("💬 Feedback? Tag me `@Vitt0c` or use this [Discord thread](https://discord.com/channels/880987707214544966/1087607534967341087/1087607534967341087)")
general_info3.markdown("☕ Donations Wallet: `0x24C262a7c49F8BBc889688A0cb0Fea97d04839c5`")    
#features_info.write(f" - 💎 Farm Worth  - 🏝️ Farm Resources \n - 🚜 Hoarder Limit - 🤑 Spent Checker \n - 👜 Basket Checker - 💰 SFL Balance \n - 🍒 Fruits Harvest Left  - 👨‍🌾 Bumpkins Stats \n - 🐔 Mutant Chickens ")

skills_description = {
"Green Thumb": "Crops yield 5% more", "Cultivator": "Crops grow 5% quicker", "Master Farmer": "Crops yield 10% more", "Golden Flowers": "Chance for Sunflowers to Drop Gold",
"Happy Crop": "Chance to get 2x crops", "Plant Whisperer": "???", "Lumberjack": "Trees drop 10% more", "Tree Hugger": "Trees regrow 20% quicker", "Tough Tree": "Chance to get 3x wood drops",
"Money Tree": "Chance for SFL drops", "Digger": "Stone Drops 10% more", "Coal Face": "Stones recover 20% quicker", "Gold Rush": "Chance to get 2.5x gold drops", "Seeker": "Attract Rock Monsters",
"Rush Hour": "Cook meals 10% faster", "Kitchen Hand": "Meals yield an extra 5% experience", "Michelin Stars": "High quality food, earn additional 5% SFL", "Curer": "Consuming deli goods adds extra 15% exp",
"Stable Hand": "Animals produce 10% quicker", "Free Range": "Animals produce 10% more", "Horse Whisperer": "Increase chance of mutants", "Buckaroo": "Chance of double drops"
}        

xp_dict = {
1: {'Level': 1, 'XP_next': 5, 'Total XP': 0}, 2: {'Level': 2, 'XP_next': 65, 'Total XP': 5}, 3: {'Level': 3, 'XP_next': 160, 'Total XP': 70}, 4: {'Level': 4, 'XP_next': 395, 'Total XP': 230},
5: {'Level': 5, 'XP_next': 875, 'Total XP': 625}, 6: {'Level': 6, 'XP_next': 1900, 'Total XP': 1500}, 7: {'Level': 7, 'XP_next': 3600, 'Total XP': 3400}, 8: {'Level': 8, 'XP_next': 4000, 'Total XP': 7000},
9: {'Level': 9, 'XP_next': 4500, 'Total XP': 11000}, 10: {'Level': 10, 'XP_next': 4500, 'Total XP': 15500}, 11: {'Level': 11, 'XP_next': 5000, 'Total XP': 20000}, 12: {'Level': 12, 'XP_next': 5500, 'Total XP': 25000},            
13: {'Level': 13, 'XP_next': 6000, 'Total XP': 30500}, 14: {'Level': 14, 'XP_next': 7500, 'Total XP': 36500}, 15: {'Level': 15, 'XP_next': 8000, 'Total XP': 44000}, 16: {'Level': 16, 'XP_next': 8500, 'Total XP': 52000},
17: {'Level': 17, 'XP_next': 9000, 'Total XP': 60500}, 18: {'Level': 18, 'XP_next': 10000, 'Total XP': 69500}, 19: {'Level': 19, 'XP_next': 10500, 'Total XP': 79500}, 20: {'Level': 20, 'XP_next': 10500, 'Total XP': 90000},
21: {'Level': 21, 'XP_next': 11000, 'Total XP': 100500}, 22: {'Level': 22, 'XP_next': 11500, 'Total XP': 111500}, 23: {'Level': 23, 'XP_next': 12500, 'Total XP': 123000}, 24: {'Level': 24, 'XP_next': 13000, 'Total XP': 135500},
25: {'Level': 25, 'XP_next': 13500, 'Total XP': 148500}, 26: {'Level': 26, 'XP_next': 14000, 'Total XP': 162000}, 27: {'Level': 27, 'XP_next': 14500, 'Total XP': 176000}, 28: {'Level': 28, 'XP_next': 15000, 'Total XP': 190500},
29: {'Level': 29, 'XP_next': 15000, 'Total XP': 205500}, 30: {'Level': 30, 'XP_next': 16000, 'Total XP': 220500}, 31: {'Level': 31, 'XP_next': 18000, 'Total XP': 236500}, 32: {'Level': 32, 'XP_next': 20000, 'Total XP': 254500},
33: {'Level': 33, 'XP_next': 22000, 'Total XP': 274500}, 34: {'Level': 34, 'XP_next': 24000, 'Total XP': 296500}, 35: {'Level': 35, 'XP_next': 28000, 'Total XP': 320500}, 36: {'Level': 36, 'XP_next': 32000, 'Total XP': 348500},
37: {'Level': 37, 'XP_next': 36000, 'Total XP': 380500}, 38: {'Level': 38, 'XP_next': 40000, 'Total XP': 416500}, 39: {'Level': 39, 'XP_next': 44000, 'Total XP': 456500}, 40: {'Level': 40, 'XP_next': 48000, 'Total XP': 500500},
41: {'Level': 41, 'XP_next': 53000, 'Total XP': 548500}, 42: {'Level': 42, 'XP_next': 58000, 'Total XP': 601500}, 43: {'Level': 43, 'XP_next': 63000, 'Total XP': 659500}, 44: {'Level': 44, 'XP_next': 68000, 'Total XP': 722500},
45: {'Level': 45, 'XP_next': 78000, 'Total XP': 790500}, 46: {'Level': 46, 'XP_next': 88000, 'Total XP': 868500}, 47: {'Level': 47, 'XP_next': 98000, 'Total XP': 956500}, 48: {'Level': 48, 'XP_next': 108000, 'Total XP': 1054500},
49: {'Level': 49, 'XP_next': 118000, 'Total XP': 1162500}, 50: {'Level': 50, 'XP_next': None, 'Total XP': 1280500}
}        

wearables_sfl = {
"Basic Hair": 5, "Rancher Hair": 5, "Red Farmer Shirt": 5, "Black Farmer Boots": 5, "Farmer Pitchfork": 5, "Sun Spots": 5,
"Explorer Hair": 5, "Blue Farmer Shirt": 5, "Farmer Overalls": 5, "Brown Boots": 5, "Axe": 5, "Brown Long Hair": 5, "Blondie": 5,
"Yellow Farmer Shirt": 5, "Lumberjack Overalls": 5, "Brown Suspenders": 5, "Yellow Boots": 5, "Buzz Cut": 5, "Parlour Hair": 5,
"Sword": 5, "Blue Suspenders": 5, "Forest Background": 5, "Beige Farmer Potion": 5, "Light Brown Farmer Potion": 5, "Dark Brown Farmer Potion": 5,
"Farmer Pants": 10, "Farm Background": 5, "Seashore Background": 5, "White Long Hair": 10, "Goblin Potion": 50
}

inventory_items = ["Dawn Breaker Ticket","Wood", "Stone", "Iron", "Gold", "Egg", "Sunflower", "Potato", "Pumpkin", "Carrot", "Cabbage", "Beetroot", "Cauliflower", "Parsnip", "Eggplant", "Radish", "Wheat", "Kale", "Apple", "Orange", "Blueberry"]
emojis = {"Block Buck": " 🎟️ ", "Dawn Breaker Ticket": " 🎟️ ", "Wood": " \U0001F332 ", "Stone": " \U000026AA ", "Iron": " \U0001F7E0 ", "Gold": " \U0001F7E1 ", "Egg": " \U0001F95A ", "Sunflower": " \U0001F33B ", "Potato":" \U0001F954 ", "Pumpkin": " \U0001F383 ", "Carrot": " \U0001F955 ", "Cabbage": " \U0001F337 ", "Beetroot": " \U0001f49c ","Cauliflower": " \U0001F90D ", "Parsnip": " \U0001F49B ", "Eggplant": " 🍆 ", "Radish": " \u2764\uFE0F ", "Wheat": " \U0001f33e ", "Kale": " 🥦 ", "Apple": " \U0001F34E ", "Orange": " \U0001f34a ", "Blueberry": " \U0001f347 "}
limits = {"Dawn Breaker Ticket": 750, "Wood": 1500, "Stone": 500, "Iron": 400, "Gold": 90, "Egg": 400, "Sunflower": 9000, "Potato": 5000, "Pumpkin": 3000, "Carrot": 2000, "Cabbage": 1500, "Beetroot": 1500, "Cauliflower": 1000, "Parsnip": 850, "Eggplant": 600, "Radish": 500, "Wheat": 500, "Kale": 500, "Apple": 200, "Orange": 200, "Blueberry": 200}

fruits = ["Apple", "Orange", "Blueberry"]
fruits_price = {"Apple": 0.3125, "Orange": 0.225, "Blueberry": 0.15}
fruit_emojis = {"Apple": " \U0001F34E ", "Orange": " \U0001f34a ", "Blueberry": " \U0001f347 "}


tab5, tab6, tab7, tab8 = st.tabs(["💾HOME", "🏆RANKING", "👥BUMPKIN", "📜NFT LIST"]) #"👨‍🔬CALCULATOR", "💸TRADER"

with tab5:
    # Define default farm ID
    DEFAULT_FARM_ID = ""

    # Get farm ID from query parameters
    app_state = st.experimental_get_query_params()
    FarmID = app_state.get("farm", [DEFAULT_FARM_ID])[0]


    st.markdown("##### 🔻 SEARCH FARM ID 🔻")
    col, buff = st.columns([2,4.5])
    with col:
        col_search2, col_ok2 = st.columns([2,2])
        with col_search2:
            farm_id = st.text_input('write your farm ID', max_chars=6, key="farm-input", label_visibility="collapsed", value= FarmID )
        with col_ok2:
            buttonok = st.button('OK')             

    status_ok = st.container() 

    url = f"https://api.sunflower-land.com/visit/{farm_id}"
    try:
        if buttonok:
            app_state["farm"] = farm_id
            st.experimental_set_query_params(**app_state)
            response = requests.get(url)
            tab1, tab2, tab3 = st.tabs(["🏡FARM ", "👨‍🌾BUMPKIN ", "💎WORTH "])

            with tab1:
                col1, col2, col3 = st.columns([3, 3, 3], gap="medium")
                with col1:
                   hoarder = st.expander("\U0001F69C **HOARDER LIMITS**", expanded=True)
                   spend = st.expander("🤑 **SPENT CHECKER**", expanded=False)
                   dawn_breaker =  st.expander("🌄 **Dawn Breaker**", expanded=True)
                with col2:
                   farm_info = st.expander("🏝️ **FARM RESOURCES**", expanded=True)
                   farm_delivery = st.expander("🚚 **DELIVERIES**", expanded=True)
                   c_mutant = st.expander("\U0001F414 **MUTANT CHICKENS DROP**", expanded=True)
                   h_fruit = st.expander("\U0001f352 **FRUIT HARVEST LEFT**", expanded=True)   
                with col3:
                   farm_ti = st.expander("☠️ **TREASURE ISLAND**", expanded=True) 
                   balance_check = st.expander("💰 **SFL BALANCE**", expanded=True)
                   basket_how = st.expander("📝 **HOW IT WORKS?**", expanded=False)  
                   basket_info = st.expander("👜  **INVENTORY CHECKER**", expanded=True)  

            with tab2:
                status_bumpkin = st.container()
                col14, col15, col16, col17 = st.columns([2, 2, 2, 2], gap="medium")
                with col14:            
                   bump_info = st.expander("🖼️ PICTURE", expanded=True)  
                   bump_worth_how = st.expander("📝 **HOW IT WORKS?**", expanded=False)  
                with col15:            
                   bump_general = st.expander("📖 **GENERAL**", expanded=True)
                with col16:
                   bump_wearables = st.expander("👖 **WEARABLES**", expanded=True)
                with col17:
                   bum_skill = st.expander("🏹 **SKILLS & ACHIEVEMENTS**", expanded=True)             

                st.divider()   

                col4, col5, col6, col7 = st.columns([2, 2, 2, 2], gap="medium")
                with col4:
                   gather = st.expander("⚒️ **RESOURCES**", expanded=True)
                   harvest = st.expander("🌱 **CROPS/FRUITS**", expanded=True) 
                with col5:
                   dug = st.expander("🏴‍☠️ **TREASURE ISLAND**", expanded=True)
                with col6:
                   bum_cook = st.expander("👨‍🍳 **MEALS COOKED**", expanded=True)      
                with col7:
                   food = st.expander("🍲 **MEALS FED**", expanded=True)

            with tab3:
                col8, col9, col10, col11 = st.columns([2, 2, 2, 2], gap="medium")
                with col8:
                    farm_worth_how = st.expander("📝 **HOW IT WORKS?**", expanded=False)
                    farm_worth = st.expander("💎 **TOTAL WORTH ESTIMATE**", expanded=True)                
                    farm_worth_skill = st.expander("🗝️ **LEGACY SKILL**", expanded=True)  
                with col9:
                    farm_worth_nft = st.expander("💸 **TRADABLES NFT'S**", expanded=True)  
                with col10:
                    farm_worth_exp = st.expander("🏝️ **EXPANSIONS**", expanded=True)
                    farm_worth_bui = st.expander("🏗️ **BUILDINGS**", expanded=True)                
                with col11:
                    farm_worth_bump = st.expander("👨‍🌾 **BUMPKIN WORTH ESTIMATE**", expanded=True) 
                    farm_worth_decorative = st.expander("🗿 **EXTRAS**", expanded=True)




            #buildings_dict = "Workbench:{}, Water Well:{}, Kitchen:{}, Tent:{}, Hen House:{}, Hen House2:{}, Bakery:{}, Smoothie Shack:{}, Deli:{}, Warehouse:{}, Toolshed:{}"
            building_items = ["Toolshed", "Warehouse", "Deli", "Smoothie Shack", "Bakery", "Hen House2", "Hen House", "Tent", "Kitchen", "Water Well"]
            building_items_resources = {
                "Toolshed": {"Wood": 500, "Iron": 30, "Gold": 25, "Axe": 100, "Pickaxe": 50},
                "Warehouse": {"Wood": 250, "Stone": 150, "Potato": 5000, "Pumpkin": 2000, "Wheat": 500, "Kale": 100},
                "Deli": {"Wood": 50, "Stone": 50, "Gold": 10, "SFL": 3.75},
                "Smoothie Shack": {"Wood": 25, "Stone": 25, "Iron": 10},
                "Bakery": {"Wood": 50, "Stone": 20, "Gold": 5, "SFL": 2.5},
                "Hen House2": {"Egg": 300, "Wood": 200, "Iron": 15, "Gold": 15, "SFL": 10},
                "Hen House": {"Wood": 30, "Iron": 5, "Gold": 5, "SFL": 1.25},
                "Tent": {"Wood": 50, "SFL": 0.0625},
                "Kitchen": {"Wood": 30, "Stone": 5, "SFL": 0.125},
                "Water Well": {"Wood": 5, "Stone": 5, "SFL": 1}
            }     

            wood_price_converted = get_resource_price(601)
            stone_price_converted = get_resource_price(602)
            iron_price_converted = get_resource_price(603)
            gold_price_converted = get_resource_price(604)
            egg_price_converted = get_resource_price(605)

            resources_items = ["Gold", "Iron", "Stone", "Wood", "Egg"]

            expansions = {
            "expansion_3": {"crops": 13, "trees": 3, "stones": 2, "iron": 0, "gold": 0, "fruitPatches": 0},
            "expansion_4": {"crops": 17, "trees": 4, "stones": 3, "iron": 1, "gold": 0, "fruitPatches": 0},
            "expansion_5": {"crops": 21, "trees": 5, "stones": 4, "iron": 2, "gold": 1, "fruitPatches": 0},
            "expansion_6": {"crops": 25, "trees": 6, "stones": 5, "iron": 2, "gold": 1, "fruitPatches": 0},
            "expansion_7": {"crops": 27, "trees": 7, "stones": 6, "iron": 3, "gold": 1, "fruitPatches": 0},
            "expansion_8": {"crops": 29, "trees": 8, "stones": 7, "iron": 3, "gold": 2, "fruitPatches": 0},
            "expansion_9A": {"crops": 29, "trees": 8, "stones": 7, "iron": 4, "gold": 2, "fruitPatches": 1},
            "expansion_9B": {"crops": 31, "trees": 9, "stones": 8, "iron": 4, "gold": 3, "fruitPatches": 0},
            "expansion_9C": {"crops": 31, "trees": 10, "stones": 8, "iron": 3, "gold": 2, "fruitPatches": 1},
            "expansion_10A": {"crops": 31, "trees": 9, "stones": 8, "iron": 5, "gold": 3, "fruitPatches": 1},
            "expansion_10B": {"crops": 31, "trees": 10, "stones": 8, "iron": 4, "gold": 2, "fruitPatches": 2},
            "expansion_10C": {"crops": 31, "trees": 9, "stones": 8, "iron": 5, "gold": 3, "fruitPatches": 1},
            "expansion_10D": {"crops": 33, "trees": 11, "stones": 9, "iron": 4, "gold": 3, "fruitPatches": 1},
            "expansion_10E": {"crops": 31, "trees": 10, "stones": 8, "iron": 4, "gold": 2, "fruitPatches": 2},
            "expansion_10F": {"crops": 33, "trees": 11, "stones": 9, "iron": 4, "gold": 3, "fruitPatches": 1},
            "expansion_11": {"crops": 33, "trees": 11, "stones": 9, "iron": 5, "gold": 3, "fruitPatches": 2},
            "expansion_12A": {"crops": 33, "trees": 11, "stones": 10, "iron": 5, "gold": 3, "fruitPatches": 4},
            "expansion_12B": {"crops": 35, "trees": 11, "stones": 10, "iron": 6, "gold": 4, "fruitPatches": 3},
            "expansion_12C": {"crops": 35, "trees": 12, "stones": 10, "iron": 5, "gold": 3, "fruitPatches": 2},
            "expansion_13A": {"crops": 35, "trees": 11, "stones": 11, "iron": 6, "gold": 1, "fruitPatches": 5},
            "expansion_13B": {"crops": 35, "trees": 12, "stones": 11, "iron": 5, "gold": 3, "fruitPatches": 4},
            "expansion_13C": {"crops": 35, "trees": 11, "stones": 11, "iron": 6, "gold": 4, "fruitPatches": 5},
            "expansion_13D": {"crops": 37, "trees": 12, "stones": 11, "iron": 6, "gold": 4, "fruitPatches": 3},
            "expansion_13E": {"crops": 35, "trees": 12, "stones": 11, "iron": 5, "gold": 3, "fruitPatches": 5},
            "expansion_13F": {"crops": 37, "trees": 12, "stones": 11, "iron": 6, "gold": 4, "fruitPatches": 3},
            "expansion_14": {"crops": 37, "trees": 12, "stones": 12, "iron": 6, "gold": 4, "fruitPatches": 5},
            "expansion_15A": {"crops": 37, "trees": 12, "stones": 12, "iron": 7, "gold": 5, "fruitPatches": 6},
            "expansion_15B": {"crops": 37, "trees": 13, "stones": 12, "iron": 6, "gold": 4, "fruitPatches": 6},
            "expansion_15C": {"crops": 39, "trees": 13, "stones": 13, "iron": 6, "gold": 4, "fruitPatches": 6},
            "expansion_16A": {"crops": 37, "trees": 13, "stones": 12, "iron": 7, "gold": 5, "fruitPatches": 7},
            "expansion_16B": {"crops": 39, "trees": 13, "stones": 13, "iron": 7, "gold": 5, "fruitPatches": 7},
            "expansion_16C": {"crops": 37, "trees": 13, "stones": 12, "iron": 7, "gold": 5, "fruitPatches": 7},
            "expansion_16D": {"crops": 39, "trees": 14, "stones": 13, "iron": 6, "gold": 4, "fruitPatches": 7},
            "expansion_16E": {"crops": 39, "trees": 13, "stones": 13, "iron": 7, "gold": 5, "fruitPatches": 7},
            "expansion_16F": {"crops": 39, "trees": 14, "stones": 13, "iron": 6, "gold": 4, "fruitPatches": 7},
            "expansion_17": {"crops": 39, "trees": 14, "stones": 13, "iron": 7, "gold": 5, "fruitPatches": 8},
            "expansion_18A": {"crops": 41, "trees": 14, "stones": 13, "iron": 7, "gold": 5, "fruitPatches": 8},
            "expansion_18B": {"crops": 41, "trees": 14, "stones": 13, "iron": 7, "gold": 5, "fruitPatches": 9},
            "expansion_18C": {"crops": 39, "trees": 15, "stones": 14, "iron": 8, "gold": 5, "fruitPatches": 9},
            "expansion_19A": {"crops": 43, "trees": 14, "stones": 13, "iron": 7, "gold": 5, "fruitPatches": 9},
            "expansion_19B": {"crops": 41, "trees": 15, "stones": 14, "iron": 8, "gold": 5, "fruitPatches": 9},
            "expansion_19C": {"crops": 43, "trees": 14, "stones": 13, "iron": 7, "gold": 5, "fruitPatches": 9},
            "expansion_19D": {"crops": 41, "trees": 15, "stones": 14, "iron": 8, "gold": 5, "fruitPatches": 10},
            "expansion_19E": {"crops": 41, "trees": 15, "stones": 14, "iron": 8, "gold": 5, "fruitPatches": 9},
            "expansion_19F": {"crops": 41, "trees": 15, "stones": 14, "iron": 8, "gold": 5, "fruitPatches": 10},
            "expansion_20": {"crops": 43, "trees": 15, "stones": 14, "iron": 8, "gold": 5, "fruitPatches": 10}
            }

            expansions_cost = {
            "expansion_3": {},
            "expansion_4": {"Stone": 1},
            "expansion_5": {"Stone": 5, "Iron": 1},
            "expansion_6": {"Stone": 10, "Iron": 2},
            "expansion_7": {"Stone": 10, "Iron": 2, "Gold": 1},
            "expansion_8": {"Stone": 25, "Gold": 3},
            "expansion_9": {"Wood": 100, "Stone": 40, "Iron": 5},
            "expansion_10": {"Wood": 100, "Stone": 50, "Iron": 5, "Gold": 2},
            "expansion_11": {"Gold": 10},
            "expansion_12": {"Wood": 500, "Stone": 20, "Gold": 2},
            "expansion_13": {"Wood": 100, "Stone": 150, "Gold": 5},
            "expansion_14": {"Wood": 40, "Stone": 30, "Iron": 10, "Gold": 10},
            "expansion_15": {"Wood": 200, "Gold": 15},
            "expansion_16": {"Stone": 150, "Iron": 30, "Gold": 10},
            "expansion_17": {"Wood": 200, "Stone": 50, "Gold": 25},
            "expansion_18": {"Wood": 300, "Stone": 200, "Iron": 30, "Gold": 10},
            "expansion_19": {"Wood": 100, "Stone": 250, "Gold": 30},
            "expansion_20": {"Wood": 1000, "Stone": 100, "Iron": 10, "Gold": 25}            
            }

            helios_sfl = {'Cactus': 0.25, ' Basic Bear': 0.625, 'Potted Potato': 0.625, 'Potted Pumpkin': 2.5, 'Potted Sunflower': 0.25, 'White Tulips': 0.25, 'Dirt Path': 0.625}

            nft_resources = {
            'Immortal Pear': {'SFL': 6.875, 'Gold': 5},
            'Treasure Map': {'Gold': 5, 'SFL': 3.28},
            'Fence': {'SFL': 0.125, 'Wood': 5},
            'Bush': {'SFL': 1.25, 'Wood': 5},
            'Shrub': {'SFL': 0.625, 'Wood': 3}
            }

            mutant_items = {"Rich Chicken", "Fat Chicken", "Speed Chicken", "Ayam Cemani"}

            crop_items = {"Sunflower", "Potato", "Pumpkin", "Carrot", "Cabbage", "Beetroot", "Cauliflower", "Parsnip", "Radish", "Wheat", "Kale"}
            crop_price = {"Sunflower": 0.000250, "Potato": 0.00175, "Pumpkin": 0.0050, "Carrot": 0.0100, "Cabbage": 0.0188, "Beetroot": 0.0350, "Cauliflower": 0.053, "Parsnip": 0.081, "Radish": 0.119, "Wheat": 0.088, "Kale": 0.125}
            bounty_items = {"Crab", "Sea Cucumber", "Seaweed", "Starfish", "Wooden Compass", "Pipi","Clam Shell", "Coral", "Pearl", "Pirate Bounty"}
            bounty_price = {"Crab": 0.1875, "Sea Cucumber": 0.28125, "Seaweed": 0.9375, "Starfish": 1.40625, "Wooden Compass": 1.64062, "Pipi": 2.34375, "Clam Shell": 4.6875, "Coral": 18.75, "Pearl": 46.875, "Pirate Bounty": 93.75}
            tool_items = {"Axe","Pickaxe","Stone Pickaxe","Iron Pickaxe","Rusty Shovel","Sand Shovel","Sand Drill"}
            tool_price ={"Axe": 0.0625, "Pickaxe": 0.0625, "Stone Pickaxe": 0.0625, "Iron Pickaxe": 0.25, "Rusty Shovel": 0.0625, "Sand Shovel": 0.0625, "Sand Drill": 0.125}
            food_items = {"Mashed Potato","Pumpkin Soup","Bumpkin Broth","Boiled Eggs","Kale Stew","Mushroom Soup","Reindeer Carrot","Kale Omelette","Cabbers n Mash","Roast Veggies","Bumpkin Salad","Goblin's Treat","Cauliflower Burger","Pancakes","Club Sandwich","Mushroom Jacket Potatoes","Sunflower Crunch","Bumpkin Roast","Goblin Brunch","Fruit Salad","Sunflower Cake","Potato Cake","Pumpkin Cake","Carrot Cake","Cabbage Cake","Beetroot Cake","Cauliflower Cake","Parsnip Cake","Radish Cake","Wheat Cake","Apple Pie","Honey Cake","Orange Cake","Apple Juice","Orange Juice","Purple Smoothie","Power Smoothie","Bumpkin Detox","Pirate Cake"}
            food_deli_items = {"Blueberry Jam","Fermented Carrots","Sauerkraut","Fancy Fries"}
            food_xp = {"Mashed Potato": 3, "Pumpkin Soup": 24, "Bumpkin Broth": 96, "Boiled Eggs": 90, "Kale Stew": 400, "Mushroom Soup": 56, "Reindeer Carrot": 10, "Kale Omelette": 1250, "Cabbers n Mash": 250, "Roast Veggies": 170, "Bumpkin Salad": 290, "Goblin's Treat": 500, "Cauliflower Burger": 255, "Pancakes": 480, "Club Sandwich": 170, "Mushroom Jacket Potatoes": 240, "Sunflower Crunch": 50, "Bumpkin Roast": 2500, "Goblin Brunch": 2500, "Fruit Salad": 225, "Sunflower Cake": 525, "Potato Cake": 650, "Pumpkin Cake": 625, "Carrot Cake": 750, "Cabbage Cake": 860, "Beetroot Cake": 1250, "Cauliflower Cake": 1190, "Parsnip Cake": 1300, "Radish Cake": 1200, "Wheat Cake": 1100, "Apple Pie": 720, "Honey Cake": 760, "Orange Cake": 730, "Apple Juice": 500, "Orange Juice": 375, "Purple Smoothie": 310, "Power Smoothie": 775, "Bumpkin Detox": 975, "Pirate Cake": 3000}
            food_deli_xp = {"Blueberry Jam": 380, "Fermented Carrots": 250, "Sauerkraut": 500, "Fancy Fries": 1000}

            cake_and_pie_items = {'Sunflower Cake', 'Potato Cake', 'Pumpkin Cake', 'Carrot Cake', 'Cabbage Cake',
            'Beetroot Cake', 'Cauliflower Cake', 'Parsnip Cake', 'Radish Cake', 'Wheat Cake',
            'Apple Pie', 'Honey Cake', 'Orange Cake', 'Pirate Cake'}

            #for item in food_items:
            #    if "Cake" in item or "Pie" in item:
            #        cake_and_pie_items[item] = None


            crop_data = {}
            inventory_dict = {}
            skills_dict = {}
            equipped_dict = {}
            buildings_dict = {}


            food_quantity = {item: 0 for item in food_items.union(food_deli_items)}
            crop_quantity = {item: 0 for item in crop_items}
            fruit_quantity = {item: 0 for item in fruits}
            bounty_quantity = {item: 0 for item in bounty_items}
            tool_quantity = {item: 0 for item in tool_items}
            mutant_quantity = {item: 0 for item in mutant_items}

            baloon_items = {"Gold", "Iron", "Stone", "Wood", "Egg"}
            baloon_inv = {}
            baloon_quantity = {}
            total_inv_value = 0
            buildings_farm = {}
            buildings_farm_price = {}


            # Define a function to calculate the price of a building
            def get_building_price(building_name):
                building = building_items_resources.get(building_name)
                if not building:
                    return Decimal(0)
                total_price = Decimal(0)
                for item in building:
                    if item in crop_price:
                        total_price += Decimal(crop_price[item]) * Decimal(building[item])
                    elif item in tool_price:
                        total_price += Decimal(tool_price[item]) * Decimal(building[item])
                    elif item in resources_items:
                        if item == "Wood":
                            total_price += Decimal(wood_price_converted) * Decimal(building[item])
                        elif item == "Stone":
                            total_price += Decimal(stone_price_converted) * Decimal(building[item])
                        elif item == "Iron":
                            total_price += Decimal(iron_price_converted) * Decimal(building[item])
                        elif item == "Gold":
                            total_price += Decimal(gold_price_converted) * Decimal(building[item])
                        elif item == "Egg":
                            egg_price = get_resource_price(605)
                            total_price += Decimal(egg_price) * Decimal(building[item])
                    elif item == "SFL":
                        total_price += Decimal(building[item])
                return total_price

            # Define a function to calculate the price of an expansion
            def get_expansion_price(current_resources):
                total_price_exp = Decimal(0)
                for item, quantity in current_resources.items():
                    if item in resources_items:
                        if item == "Wood":
                            total_price_exp += Decimal(wood_price_converted) * Decimal(quantity)
                        elif item == "Stone":
                            total_price_exp += Decimal(stone_price_converted) * Decimal(quantity)
                        elif item == "Iron":
                            total_price_exp += Decimal(iron_price_converted) * Decimal(quantity)
                        elif item == "Gold":
                            total_price_exp += Decimal(gold_price_converted) * Decimal(quantity)
                return total_price_exp

            if response.status_code == 200:
                status_ok.success(f" ✅ Done! Farm {farm_id} loaded.")
                data = response.json()
                state = data.get("state")

                balance_get = state.get("balance")
                balance_sfl = round(float(balance_get), 2)
                if balance_sfl < 10:
                    withdraw = balance_sfl - (0.3 * balance_sfl)
                elif balance_sfl < 100:
                    withdraw = balance_sfl - (0.25 * balance_sfl)
                elif balance_sfl < 1000:
                    withdraw = balance_sfl - (0.2 * balance_sfl)
                elif balance_sfl < 5000:
                    withdraw = balance_sfl - (0.15 * balance_sfl)
                else:
                    withdraw = balance_sfl - (0.1 * balance_sfl)
                withdraw_usd = withdraw * sfl_price
                withdraw_usd_str = "{:.2f}".format(round(withdraw_usd, 2))

                balance = state.get("balance")
                prevbalance = state.get("previousBalance")
                balance_float = float(balance)
                prevbalance_float = float(prevbalance)
                daily_limit = balance_float - prevbalance_float
                inventory = state.get("inventory")
                inventory_dict = eval(str(inventory))
                buildings_str = state.get("buildings")
                buildings_dict = eval(str(buildings_str))

                dawnBreaker = state.get("dawnBreaker")
                laternsWeek = dawnBreaker.get ("lanternsCraftedByWeek")
                week1 = laternsWeek.get ("1")
                week2 = laternsWeek.get ("2")
                week3 = laternsWeek.get ("3")
                week4 = laternsWeek.get ("4")
                week5 = laternsWeek.get ("5")
                week6 = laternsWeek.get ("6")
                week7 = laternsWeek.get ("7")
                week8 = laternsWeek.get ("8")

                answered_riddle_ids = dawnBreaker.get("answeredRiddleIds")
                riddle_week_map = {
                    "hoot-dawn-breaker-week-1": week1,
                    "hoot-dawn-breaker-week-2": week2,
                    "hoot-dawn-breaker-week-3": week3,
                    "hoot-dawn-breaker-week-4": week4,
                    "hoot-dawn-breaker-week-5": week5,
                    "hoot-dawn-breaker-week-6": week6,
                    "hoot-dawn-breaker-week-7": week7,
                    "hoot-dawn-breaker-week-8": week8
                }

                bumpkin = state.get("bumpkin")
                taskcount = 0
                count_chore = 0

                if bumpkin: 
                    skills = bumpkin.get("skills")
                    skills_dict = eval(str(skills))
                    equipped = bumpkin.get("equipped")
                    equipped_dict = eval(str(equipped))
                    activity = bumpkin.get ("activity")

                    hayseed = state.get("hayseedHank")
                    completed_chore = hayseed.get("dawnBreakerChoresCompleted")
                    skip_chores = hayseed.get("dawnBreakerChoresSkipped")
                    chore = hayseed.get("chore")
                    progress_chore = hayseed.get("progress")
                    if progress_chore is None:
                        count_chore = 0 # Or whatever default value you want to use
                    else:
                        count_chore = progress_chore.get("startCount")
                    activitytask = chore.get("activity")
                    description_chore = chore.get("description")
                    reward_chore = chore.get("reward")
                    requirement_chore = chore.get("requirement")
                    item_chore = reward_chore.get("items")
                    ticket_chore = item_chore.get("Dawn Breaker Ticket")
                    taskcount = activity.get(activitytask)


                total_xp = 0
                for item, quantity in inventory_dict.items():
                    if item not in food_xp and item not in food_deli_xp:
                        continue
                    if item in food_items:
                        xp = int(food_xp[item])
                        total_xp += xp * int(quantity)
                        # Update the quantity of the food item
                        food_quantity[item] += int(quantity)
                    elif item in food_deli_items:
                        xp = int(food_deli_xp[item])
                        if "Curer" in skills_dict:
                            xp *= 1.15
                        total_xp += xp * int(quantity)
                        # Update the quantity of the food deli item
                        food_quantity[item] += int(quantity)

                if "Kitchen Hand" in skills_dict:
                    total_xp *= 1.05
                if "Observatory" in inventory_dict:
                    total_xp *= 1.05
                if "Golden Spatula" in equipped_dict.values():
                    total_xp *= 1.10

                crop_sells = 0
                for item, quantity in inventory_dict.items():
                    if item not in crop_price:
                        continue
                    if item in crop_items:
                        c_price = crop_price[item]
                        crop_sells += round(float(quantity)) * c_price
                        crop_quantity[item] += round(float(quantity))

                fruit_sells = 0
                for item, quantity in inventory_dict.items():
                    if item not in fruits_price:
                        continue
                    if item in fruits:
                        f_price = fruits_price[item]
                        fruit_sells += round(float(quantity)) * f_price
                        fruit_quantity[item] += round(float(quantity))                

                if "Green Thumb" in inventory_dict:
                    crop_sells *= 1.05

                bounty_sells = 0
                for item, quantity in inventory_dict.items():
                    if item not in bounty_price:
                        continue
                    if item in bounty_items:
                        b_price = bounty_price[item]
                        bounty_sells += int(quantity) * b_price
                        bounty_quantity[item] += int(quantity)

                if "Treasure Map" in inventory_dict:
                    bounty_sells *= 1.20

                tool_cost = 0
                for item, quantity in inventory_dict.items():
                    if item not in tool_price:
                        continue
                    if item in tool_items:
                        t_price = tool_price[item]
                        tool_cost += int(float(quantity)) * t_price
                        tool_quantity[item] += int(float(quantity))

                chickens = state.get ("chickens")
                chickens_str = str(chickens)
                chickens_dict = state["chickens"]

                for chicken in chickens_dict.values():
                    if "reward" in chicken:
                        for item in chicken["reward"]["items"]:
                            if item["name"] in mutant_items:
                                mutant_quantity[item["name"]] += item["amount"]

                resources = ["crops", "trees", "stones", "iron", "gold" , "fruitPatches"]
                totals = {}
                total_resources = totals

                for resource in resources:
                    value = state.get(resource)
                    if value is not None:
                        total = str(value).count("createdAt")
                    else:
                        total = 0
                    totals[resource] = total

                crops_str = state.get("crops")
                crops_dict = eval(str(crops_str))

                dawn_breaker_tickets_count = 0
                for crop_id, crop_info in crops_dict.items():
                    if 'crop' in crop_info:
                        crop_name = crop_info['crop']['name']
                        crop_amount = crop_info['crop']['amount']
                        if 'reward' in crop_info['crop']:
                            reward_items = crop_info['crop']['reward']['items']
                            for reward_item in reward_items:
                                if reward_item['name'] == 'Dawn Breaker Ticket':
                                    dawn_breaker_tickets_count += reward_item['amount']
                        if crop_name in crop_data:
                            crop_data[crop_name]['mentions'] += 1
                            crop_data[crop_name]['amount'] += crop_amount
                        else:
                            crop_data[crop_name] = {'mentions': 1, 'amount': crop_amount}
                    else:
                        continue

                state_json = response.json().get("state")

                num_wood = sum(1 for tree in state_json.get("trees").values() if "wood" in tree)
                total_wood_amount = sum(tree.get("wood", {}).get("amount", 0) for tree in state_json.get("trees").values())

                num_stones = sum(1 for stone in state_json.get("stones").values() if "stone" in stone)
                total_stone_amount = sum(stone.get("stone", {}).get("amount", 0) for stone in state_json.get("stones").values())

                num_iron = sum(1 for iron in state_json.get("iron").values() if "stone" in iron)
                total_iron_amount = sum(iron.get("stone", {}).get("amount", 0) for iron in state_json.get("iron").values())

                num_gold = sum(1 for gold in state_json.get("gold").values() if "stone" in gold)
                total_gold_amount = sum(gold.get("stone", {}).get("amount", 0) for gold in state_json.get("gold").values())

                num_chickens = sum(1 for chicken in state_json.get("chickens").values() if "fedAt" in chicken)
                total_chickens_amount = sum(chicken.get("multiplier", 0) for chicken in state_json.get("chickens").values() if "fedAt" in chicken)
                delivery = state.get("delivery")
                deliveryTotal = delivery.get ("fulfilledCount")
                delivery_data = delivery.get ("orders")
                treasureIsland = state.get("treasureIsland")

                bumpkin = state.get("bumpkin")
                if bumpkin:
                    bump_xp = bumpkin.get("experience")
                    bump_id = bumpkin.get("id")
                    bump_achi = bumpkin.get("achievements")
                    bump_url = bumpkin.get ("tokenUri")
                    activities = bumpkin.get("activity")
                    trees_chopped = activities.get("Tree Chopped")
                    egg_collected = activities.get("Egg Collected")
                    sandshovel = activities.get("Treasure Dug")
                    drill = activities.get("Treasure Drilled")
                    if sandshovel is not None and drill is not None:
                        dug_holes = sandshovel + drill               

                    fed_activities = {}
                    dug_activities = {}
                    cooked_activities = {}
                    harvested_activities = {}
                    harvested_fruit_activities = {"Apple Harvested", "Blueberry Harvested", "Orange Harvested"}
                    mined_activities = {}
                    fed_total = 0
                    cooked_total = 0
                    harvested_total = 0
                    fruit_total = 0

                    for activity, value in activities.items():
                        if "Fed" in activity:
                            fed_activities[activity] = value
                            fed_total += value
                        if "Dug" in activity:
                            if activity not in ["Treasure Dug"]:
                                dug_activities[activity] = value
                        if "Cooked" in activity:
                            cooked_activities[activity] = value
                            cooked_total += value
                        if "Mined" in activity:
                            mined_activities[activity] = value                
                        if "Harvested" in activity:
                            harvested_activities[activity] = value
                            if activity not in harvested_fruit_activities:
                                harvested_total += value
                            else:
                                fruit_total += value

                fruit_patches_str = state.get("fruitPatches")
                if isinstance(fruit_patches_str, str):
                    fruit_patches_dict = json.loads(fruit_patches_str)
                else:
                    fruit_patches_dict = fruit_patches_str
                fruits = {}

                balance_check.info(f"📈 SFL Current Price: **${sfl_price:.4f}**")
                #balance_check.info(f"\n 🟣 MATIC Current Price: **${matic_price:.2f}**")
                balance_check.write(f" - 💰 SFL Balance: **:green[{balance_sfl:.2f}]**")
                balance_check.write(f" - 💸 SFL After Withdraw: **:red[{withdraw:.2f}]**")
                balance_check.write("\n")
                balance_check.success(f"\n💱 Withdraw in Dolars: **${withdraw_usd_str}**")

                hoarder.info("\n \U0001F4B0  **SFL Daily Limit: [{:.2f} / 250]**".format(daily_limit))
                spend_info_written = False     

                for item in inventory_items:
                    new_inv = state.get("inventory", {}).get(item)
                    old_inv = state.get("previousInventory", {}).get(item)
                    if new_inv is not None:
                        if old_inv is None:
                            diff = int(round(float(new_inv)))
                        else:
                            diff = int(round(float(new_inv))) - int(round(float(old_inv)))
                        if diff != 0:

                            limit = limits.get(item)
                            if isinstance(diff, str) and diff.isnumeric():
                                diff = int(diff)
                            if isinstance(limit, str) and limit.isnumeric():
                                limit = int(limit)
                            if limit != 0:
                                percentage = (diff / limit) * 100
                                if percentage < 0:
                                    percentage = 0
                                percentage_float = float(percentage)
                                percentage_number = "{:.0f}".format(percentage_float)
                                percentage_final = float(percentage_number) / 100

                                if percentage > 0:
                                    hoarder.write(f" -{emojis.get(item)} {item.capitalize()}: [{diff} / {limits.get(item)}] = **{percentage_number}%**")
                                    if percentage_final > 1:
                                        percentage_final = 1.0
                                    hoarder.progress(percentage_final, text=None)
                                else:
                                    if not spend_info_written:
                                        spend.info("\n ⚠️ **Negative values means that you spent more of that resource of what you gather/harvest since your last SYNC.**")
                                        spend_info_written = True
                                    spend.write(f" -{emojis.get(item)} {item.capitalize()}: [{diff} / {limits.get(item)}]")             
                            else:
                                continue

                total_mutant = sum(mutant_quantity.values())
                if total_mutant == 0:
                    c_mutant.info("\n 🐣 **Mutants Drop: 0**")
                else:
                    c_mutant.info(f"\n 🐣 **Mutants Drop: {total_mutant}**")
                    for item in mutant_items:
                        if mutant_quantity[item] > 0:
                            c_mutant.success(f"\n 🐤 **{item}: {mutant_quantity[item]}**")

                for item in baloon_items:
                    new_inv_baloon = state.get("inventory", {}).get(item)
                    if new_inv_baloon  is not None:
                        baloon_inv[item] = new_inv_baloon 
                        baloon_quantity[item] = Decimal(new_inv_baloon)

                wood_inv_value = baloon_quantity.get("Wood", 0) * wood_price_converted
                stone_inv_value = baloon_quantity.get("Stone", 0) * stone_price_converted
                iron_inv_value = baloon_quantity.get("Iron", 0) * iron_price_converted
                gold_inv_value = baloon_quantity.get("Gold", 0) * gold_price_converted
                egg_inv_value = baloon_quantity.get("Egg", 0) * egg_price_converted


                total_npc_market = crop_sells + fruit_sells + bounty_sells
                total_npc_market_usd = Decimal(total_npc_market) * Decimal(sfl_price)
                total_baloon_market = egg_inv_value + wood_inv_value + stone_inv_value + iron_inv_value + gold_inv_value
                total_sales = Decimal(total_npc_market) + Decimal(total_baloon_market)
                total_sales_usd = Decimal(total_sales) * Decimal(sfl_price)
                total_baloon_market_usd = Decimal(total_baloon_market) * Decimal(sfl_price)

                farm_info.info(f"\n 🌱 **Crops to be Harvest:**")
                for crop_name, info in crop_data.items():
                    final_amount = round(info['amount'], 2)
                    emoji = emojis.get(crop_name, "")  
                    farm_info.write(f" - {emoji} **{final_amount:.2f} {crop_name}** — {info['mentions']}x Plots")
                if dawn_breaker_tickets_count > 0:
                    farm_info.write(f"- 🎟️ **{dawn_breaker_tickets_count} Dawn Breaker Ticket**")    

                farm_info.write("\n")   
                farm_info.success(f"\n ⚒️ **Resources to be Gathered:**")
                farm_info.write(f" - 🌲 **{total_wood_amount:.2f} Wood** — {num_wood}x Trees")
                farm_info.write(f" - ⚪ **{total_stone_amount:.2f} Stone** — {num_stones}x Stones")
                farm_info.write(f" - 🟠 **{total_iron_amount:.2f} Iron** — {num_iron}x Iron Rocks")
                farm_info.write(f" - 🟡 **{total_gold_amount:.2f} Gold** — {num_gold}x Gold Rocks")
                farm_info.write(f" - 🥚 **{total_chickens_amount:.2f} Eggs** — {num_chickens}x Chickens")


                #farm_info.write("\n")          
                #farm_info.success(f"\n 📊 **Total Nodes:**")
                #farm_info.write(f"\n - 🌱 **Plots: {totals['crops']}** - ⚪ **Stone: {totals['stones']}**")
                #farm_info.write(f"\n - 🌲 **Trees: {totals['trees']}** - 🟠 **Iron: {totals['iron']}**")        
                #farm_info.write(f"\n - 🍒 **Fruit: {totals['fruitPatches']}** --- 🟡 **Gold: {totals['gold']}**")

                lantern_name = {
                    1: "Luminous",
                    2: "Radiance",
                    3: "Aurora",
                    4: "Radiance",
                    5: "Aurora",
                    6: "Luminous",
                    7: "Ocean",
                    8: "Aurora"
                }

                riddle_reward = {
                    1: "---",
                    2: "50",
                    3: "75",
                    4: "50",
                    5: "50",
                    6: "50",
                    7: "50",
                    8: "50"
                }

                #dawn_breaker.write("\n")
                #dawn_breaker.info(f" 👨‍🌾 **HaySeed Hank:**")

                # Define progress_count with default value of 0
                progress_count = 0                

                # Check if taskcount and count_chore are not None
                if taskcount is not None and count_chore is not None:
                    progress_count = taskcount - count_chore

                if bumpkin:
                    df_weeks = []
                    for week in range(1, 9):
                        lanterns = laternsWeek.get(str(week), 0)
                        if week == 1:
                            riddle = "-----"
                        else:
                            riddle = "Yes ✅" if f"hoot-dawn-breaker-week-{week}" in answered_riddle_ids else "No ❌"
                        lantern_name_value = lantern_name.get(week, "")
                        if lanterns > 0:
                            lanterns_info = f"{lanterns} {lantern_name_value}"
                        else:
                            lanterns_info = ""
                        df_weeks.append({"Week": week, "Lanterns Crafted": lanterns_info, "Riddle Solved": riddle, "Reward 🎟️": riddle_reward.get(week, "")})

                    dfweek = pd.DataFrame(df_weeks)
                    dfweek = dfweek[dfweek["Lanterns Crafted"] != ""]  # Drop rows with empty "Lanterns Crafted" column
                    dfweek.set_index("Week", inplace=True)
                    dawn_breaker.write(dfweek)                  
                    if skip_chores is None:
                        skip_chores = 0
                    if completed_chore is None:
                        completed_chore = 0                    

                    if completed_chore < (125 - skip_chores):
                        next_loop = 125 - completed_chore - skip_chores
                    elif completed_chore < (183 - skip_chores):
                        next_loop = 183 - completed_chore - skip_chores
                    elif completed_chore < (241 - skip_chores):
                        next_loop = 241 - completed_chore - skip_chores
                    elif completed_chore < (299 - skip_chores):                
                        next_loop = 299 - completed_chore - skip_chores  
                    elif completed_chore < (357 - skip_chores):                
                        next_loop = 357 - completed_chore - skip_chores                 
                    elif completed_chore < (415 - skip_chores):                
                        next_loop = 415 - completed_chore - skip_chores
                    elif completed_chore < (473 - skip_chores):                
                        next_loop = 473 - completed_chore - skip_chores
                    else:
                        next_loop = None 
                    dawn_breaker.info(f" 🗂️ Current Quest: **{description_chore}**")
                    dawn_breaker.write(f" - 🎟️ Tickets Reward: **{ticket_chore}**")
                    dawn_breaker.write(f" - ⏳ Progress: **{progress_count} of {requirement_chore}**")
                    dawn_breaker.write("\n")
                    if next_loop is not None:
                        dawn_breaker.success(f"\n 📊 **Total Quest Completed: {completed_chore}** (Next Loop in: **{next_loop})**")
                    else:
                        dawn_breaker.success(f"\n 📊 **Total Quest Completed: {completed_chore}**")                    
                else:
                    dawn_breaker.error(f" **There aren't Bumpkins in this Farm.**")

                deliveryItemList = []
                deliveryRewardList = []
                deliveryTimeList = []

                for order in delivery_data:
                    items = order["items"]
                    reward = order["reward"]
                    readytime = order["readyAt"]

                    if items:
                        deliveryItemList.extend(list(items.keys()))

                    if reward and "items" in reward:
                        reward_items = reward["items"]
                        if reward_items:
                            deliveryRewardList.extend(list(reward_items.keys()))

                    if readytime:
                        deliveryTimeList.append(readytime)

                current_time = datetime.now().timestamp() * 1000  # Convert to milliseconds

                data = []
                if delivery_data:
                    for index, order in enumerate(delivery_data, start=1):
                        items = order.get("items")
                        reward = order.get("reward")
                        readytime = order.get("readyAt")

                        if items:
                            deliveryItems = ", ".join(items.keys())
                            deliveryItems_value = ", ".join([f"{value}x {key}" for key, value in items.items()])
                        else:
                            deliveryItems = ""
                            deliveryItems_value = ""
                        if reward and "sfl" in reward:
                            reward_sfl = reward["sfl"]
                            extra_boost = 1.0
                            if bumpkin:
                                if "Michelin Stars" in skills_dict:
                                    extra_boost *= 1.05
                                if any(item in cake_and_pie_items for item in items.keys()) and "Chef Apron" in equipped_dict.values():
                                    extra_boost += 0.20
                            reward_sfl *= extra_boost
                            deliveryReward = f"{reward_sfl:.2f} SFL"
                        else:
                            deliveryReward = ""
                        if readytime and readytime > current_time:
                            remaining_time = readytime - current_time
                            hours_remaining = int(remaining_time / (1000 * 60 * 60))  # Convert milliseconds to hours
                            minutes_remaining = int((remaining_time / (1000 * 60)) % 60)  # Convert milliseconds to minutes
                            deliveryTime = f"{hours_remaining}hrs {minutes_remaining}mins"
                        else:
                            deliveryTime = "✅ Available"
                      
                        order_status = "✅"
                        if deliveryItems_value:
                            items_list = deliveryItems_value.split(", ")
                            for item in items_list:
                                item_parts = item.split("x", 1)
                                if len(item_parts) >= 2:
                                    item_name = item_parts[1].strip()
                                    item_quantity = int(float(item_parts[0].strip()))
                                    if item_name in inventory_dict and float(inventory_dict[item_name]) >= item_quantity:
                                        continue
                                order_status = "❌"
                                break                           

                        data.append([f"{index}\uFE0F\u20E3", f"{order_status} {deliveryItems_value}", deliveryReward, deliveryTime])

                columns = ["N#", "Order and Status", "Reward", "Time"]
                df_order = pd.DataFrame(data, columns=columns)
                df_order.set_index("N#", inplace=True)
                farm_delivery.write(df_order)
                
                farm_delivery.success(f" 📊 **Total Deliveries Completed: {deliveryTotal}**")
                
                ti_dug = []
                if 'holes' in treasureIsland:
                    for i in treasureIsland["holes"]:
                        dugAt = datetime.fromtimestamp(int(str(treasureIsland["holes"][i]["dugAt"])[:10]))
                        if dugAt.date() == datetime.today().date():
                            ti_dug.append(treasureIsland["holes"][i]["discovered"])

                ti_dug_today = {}
                for i in ti_dug:
                    if str(i) in ti_dug_today:
                        ti_dug_today[str(i)] += 1
                    else:
                        ti_dug_today[str(i)] = 1

                sorted_ti_dug_today = sorted(ti_dug_today.items(), key=lambda x: x[1], reverse=True)

                df_dugs = pd.DataFrame(sorted_ti_dug_today, columns=["Rewards Dug", "Quantity"])
                df_dugs.set_index("Rewards Dug", inplace=True)    

                dug_total_count = sum(ti_dug_today.values())

                if dug_total_count > 0:
                    farm_ti.write(df_dugs)
                    farm_ti.success(f"📊 **Total Dugs Today: {dug_total_count}**")
                else:
                    farm_ti.error(f" **This farm didn't use Treasure Island today**")

                basket_how.info(f"\n **The NPC market sales is using the values of the in game shops, like the seeds shop or the Treasure Island one, to calculate the prices/cost (Includes your boost)**")
                basket_how.success("\n **The balloon sales is using the lowest listed price at the Balloon and counting the 10% Goblins fee, but it doesn't include the listing fee**")

                basket_info.info(f" 🏪 **NPC Market: {total_npc_market:.2f} SFL (${total_npc_market_usd:.2f})**")      
                basket_info.write(f" - 🌾 Crops sell: **{crop_sells:.2f} SFL**")
                basket_info.write(f" - 🍒 Fruits sell: **{fruit_sells:.2f} SFL**")
                basket_info.write(f" - 🏴‍☠️ Treasure Bountys: **{bounty_sells:.2f} SFL**")
                basket_info.write(f" - ⚒️ Tools cost: **-{tool_cost:.2f} SFL (Excluded in sales)**")
                basket_info.write("\n")  

                basket_info.info(f" 🎈 **Balloon Sales: {total_baloon_market:.2f} SFL (${total_baloon_market_usd:.2f})**")  
                basket_info.write(f" - 🥚 Eggs sell: **{egg_inv_value:.2f} SFL**")
                basket_info.write(f" - 🌲 Woods sell: **{wood_inv_value:.2f} SFL**")
                basket_info.write(f" - ⚪ Stones sell: **{stone_inv_value:.2f} SFL**")
                basket_info.write(f" - 🟠 Irons sell: **{iron_inv_value:.2f} SFL**")
                basket_info.write(f" - 🟡 Golds sell: **{gold_inv_value:.2f} SFL**")
                basket_info.write("\n")  

                basket_info.success(f" 🚀 **Total Sales: {total_sales:.2f} SFL (${total_sales_usd:.2f})**")    

                if fruit_patches_dict:
                    for patch_id, patch_data in fruit_patches_dict.items():
                        fruit = patch_data.get("fruit")
                        if not fruit:
                            continue 
                        name = fruit.get("name")
                        havlft = fruit.get("harvestsLeft")
                        if name not in fruits:
                            fruits[name] = [(patch_id, havlft)]
                        else:
                            fruits[name].append((patch_id, havlft))

                    if not fruits:
                        h_fruit.error("\n **There aren't Fruit trees.**")
                    else:
                        for name, trees in fruits.items():
                            total_harvests_left = 0
                            fruit_harvest_left_container = st.container()
                            for tree_id, tree_data in fruit_patches_dict.items():
                                if tree_data.get("fruit") and tree_data["fruit"].get("name") == name:
                                    harvests_left = tree_data["fruit"].get("harvestsLeft")
                                    total_harvests_left += harvests_left

                            with fruit_harvest_left_container:
                                h_fruit.write("\n")
                                h_fruit.info(f"\n{fruit_emojis.get(name)} **{name} Harvest Left: {total_harvests_left}**")
                                for tree_id, tree_data in fruit_patches_dict.items():
                                    if tree_data.get("fruit") and tree_data["fruit"].get("name") == name:
                                        harvests_left = tree_data["fruit"].get("harvestsLeft")
                                        h_fruit.write(f" - 🌳 **{harvests_left} Harvests Left** ")
                else:
                    h_fruit.error("\n **There aren't Fruit trees.**")

                if bumpkin:
                    image_url = bump_url.rfind("v1_")
                    if image_url != -1:
                        # Extract the substring after "v1_"
                        bump_url_last = bump_url[image_url + len("v1_"):]
                    bump_img_url = f'<img src="https://images.bumpkins.io/nfts/{bump_url_last}.png" width = 100%>'
                    # Create lists to store the keys and values               

                    bump_general.info(f" #️⃣ **Bumpkin ID: #{bump_id}**")

                    current_lvl = None
                    for level, info in xp_dict.items():
                        if bump_xp >= info['Total XP']:
                            current_lvl = level

                    if current_lvl is None:
                        current_lvl = max(xp_dict.keys())

                    if current_lvl == max(xp_dict.keys()):
                        xp_needed = 'N/A'
                        nextlvl_xp = 'N/A'
                        extra_xp = 'N/A'
                    else:
                        if current_lvl in xp_dict:
                            level_info = xp_dict[current_lvl]
                            xp_needed = level_info['XP_next'] - (bump_xp - level_info['Total XP'])
                            nextlvl_xp = level_info['XP_next']
                            extra_xp = nextlvl_xp - xp_needed
                        else:
                            xp_needed = 'N/A'
                            nextlvl_xp = 'N/A'
                            extra_xp = 'N/A'

                    new_total_xp = bump_xp + total_xp  

                    new_lvl = None
                    for level, info in xp_dict.items():
                        if new_total_xp >= info['Total XP']:
                            new_lvl = level

                    if new_lvl is None:
                        new_lvl = max(xp_dict.keys())

                    if new_lvl == max(xp_dict.keys()):
                        new_xp_needed = 'N/A'
                        new_nextlvl_xp = 'N/A'
                        new_extra_xp = 'N/A'
                    else:
                        if new_lvl in xp_dict:
                            level_info = xp_dict[new_lvl]
                            new_xp_needed = level_info['XP_next'] - (new_total_xp - level_info['Total XP'])
                            new_nextlvl_xp = level_info['XP_next']
                            new_extra_xp = new_nextlvl_xp - new_xp_needed
                        else:
                            new_xp_needed = 'N/A'
                            new_nextlvl_xp = 'N/A'
                            new_extra_xp = 'N/A'
                    level_price = (bump_xp / 500) * sfl_price
                      # Check if the values are floats before rounding
                    if isinstance(new_xp_needed, float):
                        new_xp_needed = round(new_xp_needed, 1)
                    if isinstance(new_nextlvl_xp, float):
                        new_nextlvl_xp = round(new_nextlvl_xp, 1)
                    if isinstance(new_extra_xp, float):
                        new_extra_xp = round(new_extra_xp, 1)
                    filtered_df = wearable_list(equipped_dict, return_type='filtered_df')
                    total_value_wearable = wearable_list(equipped_dict, return_type='total')
                    bump_price_usd = total_value_wearable + level_price


                    bump_info.markdown(bump_img_url, unsafe_allow_html = True) 
                    bump_info.write("\n")
                    bump_info.success(f"\n📊 Total Worth Estimate: **${bump_price_usd:.2f}**")

                    bump_worth_how.error(f"**Note that this info in linked to the last state of the bumpkin in that farm, if the player changed the wearables and didn't log again in their farm the info is going to be outdated, you can use the Bumpkin ID search to see the current state.**")   
                    bump_worth_how.info(f'The value of **Levels Price** are calculated using **500 XP = 1 SFL**, considering this kinda as average value cost of the most used meals XP and lowered a little bit to also **"value the time"**.')
                    bump_worth_how.success(f"For **Bumpkin Wearables**, it uses the **average between the last sold price and the current lowest listing price on Opensea**, which is updated 1-2 times per day (semi-manually).")

                    bump_general.write(f" - 📗 Current Level: **{current_lvl}**")
                    bump_general.write(f" - 📘 Current Total XP: **{round(bump_xp, 1)}**")
                    if current_lvl == max(xp_dict.keys()):
                        bump_general.write(f" - 📙 Current Progress: **(MAX)**")
                        bump_general.write(f" - ⏭️ XP for Next LVL: **(MAX)**")
                    else:                       
                        bump_general.write(f" - 📙 Current Progress: **[{round(extra_xp, 1)} / {nextlvl_xp}]**")
                        bump_general.write(f" - ⏭️ XP for Next LVL: **{round(xp_needed, 1)}**")
                    bump_general.write("\n")
                    bump_general.success(f"\n📊 Levels Price Estimate: **${level_price:.2f}**") 

                    total_quantity = sum(food_quantity.values())
                    bump_general.write(f" - 🍲 Quantity of Meals: **{total_quantity}**")
                    bump_general.write(f"\n - 🔼 Total XP from Meals: **{total_xp:.2f}**")

                    bump_general.write("\n")
                    if new_lvl == max(xp_dict.keys()):
                        bump_general.info(f" 📚 Level after Eating: **{new_lvl} (MAX)**")
                    else:
                        bump_general.info(f" 📚 Level after Eating: **{new_lvl} - [{new_extra_xp} / {new_nextlvl_xp}]**") 
                    bump_general.success(f" 📊 New Total XP: **{new_total_xp:.1f}**")

                    bump_wearables.write(filtered_df)
                    bump_wearables.success(f"\n📊 Wearables Total Price: **${total_value_wearable:.2f}**")            

                    # Create lists to store the keys and descriptions
                    skill_names = []
                    skill_descriptions = []

                    # Iterate over the dictionary and extract the keys and descriptions
                    for key in skills_dict:
                        skill_names.append(key)
                        skill_descriptions.append(skills_description.get(key, "Description not available"))
                    # Create a DataFrame
                    df_skills = pd.DataFrame({"Skill": skill_names, "Description": skill_descriptions})
                    df_skills.set_index("Skill", inplace=True)

                    # Write the DataFrame
                    bum_skill.write(df_skills)
                    bump_achi_total = len(bump_achi)
                    bum_skill.success(f"\n🏅 Total Achivements: **{bump_achi_total}**")               

                    gathe_activity_values = [("Trees Chopped", trees_chopped)] + [(activity, value) for activity, value in mined_activities.items()] + [("Eggs", egg_collected)]
                    df_gather = pd.DataFrame(gathe_activity_values, columns=["Activity", "Value"])
                    df_gather.set_index("Activity", inplace=True)
                    gather.write(df_gather)

                    harvest.info(f"🌾 **Total Crops Harvested: {harvested_total}**")
                    harvest.success(f"🍒 **Total Fruits Harvested: {fruit_total}**")
                    harvest_activity_values = [(activity, value) for activity, value in harvested_activities.items()]
                    harvest_sorted_activity_values = sorted(harvest_activity_values, key=lambda x: x[1], reverse=True)
                    harvest_df_activities = pd.DataFrame(harvest_sorted_activity_values, columns=["Activity", "Value"])
                    harvest_df_activities.set_index("Activity", inplace=True)
                    harvest.write(harvest_df_activities)                


                    dug.info(f"🔵 **Total Sand Shovel Used: {sandshovel}**")
                    dug.info(f"🟤 **Total Sand Drill Used: {drill}**")
                    if sandshovel is not None and drill is not None:
                        dug.success(f"📊 **Total Holes Dug: {dug_holes}**")
                    dug_activity_values = [(activity, value) for activity, value in dug_activities.items()]
                    dug_sorted_activity_values = sorted(dug_activity_values, key=lambda x: x[1], reverse=True)
                    dug_df_activities = pd.DataFrame(dug_sorted_activity_values, columns=["Activity", "Value"])
                    dug_df_activities.set_index("Activity", inplace=True)
                    dug.write(dug_df_activities)                

                    bum_cook.info(f"🍳 **Total Meals Cooked: {cooked_total}**")
                    cook_activity_values = [(activity, value) for activity, value in cooked_activities.items()]
                    cook_sorted_activity_values = sorted(cook_activity_values, key=lambda x: x[1], reverse=True)
                    cook_df_activities = pd.DataFrame(cook_sorted_activity_values, columns=["Activity", "Value"])
                    cook_df_activities.set_index("Activity", inplace=True)
                    bum_cook.write(cook_df_activities)   

                    food.info(f"🤤 **Total Meals Fed: {fed_total}**")            
                    activity_values = [(activity, value) for activity, value in fed_activities.items()]
                    sorted_activity_values = sorted(activity_values, key=lambda x: x[1], reverse=True)
                    df_activities = pd.DataFrame(sorted_activity_values, columns=["Activity", "Value"])
                    df_activities.set_index("Activity", inplace=True)
                    food.write(df_activities)
                else:
                    status_bumpkin.error(f" **There aren't Bumpkins in this Farm.**")

                expansion_resources = ["Wood", "Stone", "Iron", "Gold"]
                previous_resources = {}

                for expansion, resources in expansions.items():
                    if not resources:
                        expansion_num = int(expansion.split("_")[1].rstrip("ABCDEF"))
                        farm_worth_exp.info(f"🔼 **This Farm is in the Expansion {expansion_num}**")
                        continue  # move on to the next expansion

                    for key, value in total_resources.items():
                        if key not in resources or value > resources[key]:
                            break
                    else:
                        expansion_num = int(expansion.split("_")[1].rstrip("ABCDEF"))
                        farm_worth_exp.info(f"🔼 **This Farm is in the Expansion {expansion_num}**")
                        break

                total_price_exp = Decimal(0)
                for i in range(3, expansion_num + 1):
                    expansion_key = f"expansion_{i}"
                    resources = expansions_cost[expansion_key]
                    current_resources = {}
                    for resource in expansion_resources:
                        current_resources[resource] = resources.get(resource, 0) + previous_resources.get(resource, 0)
                    previous_resources = current_resources
                    expansion_price = get_expansion_price(current_resources)
                    expansion_price_usd = Decimal(expansion_price) * Decimal(sfl_price)
                    total_price_exp += expansion_price_usd

                total_price = 0  
                total_price_usd = 0 

                for building in building_items:
                    if "Hen House" in building:
                        if "Hen House" in buildings_dict:
                            building_count = sum(1 for b in buildings_dict["Hen House"] if "createdAt" in b)
                            if building_count > 1:
                                buildings_dict["Hen House2"] = buildings_dict["Hen House"][-1:]
                                buildings_dict["Hen House"] = buildings_dict["Hen House"][:-1]
                                building_items.append("Hen House2")
                    else:
                        continue

                data_buildings = []

                if not any(building in buildings_dict for building in building_items):
                    farm_worth_bui.error("There aren't buildings")
                else:
                    for building in building_items:
                        if building in buildings_dict:
                            if buildings_dict[building]:
                                building_count = sum(1 for b in buildings_dict[building] if "createdAt" in b)
                            else:
                                building_count = 1
                            building_price = get_building_price(building)
                            if building == "Hen House2" and "Hen House2" in buildings_farm:
                                continue
                            buildings_farm[building] = buildings_dict[building]
                            buildings_farm_price[building] = building_price
                            total_building_price = building_price * Decimal(building_count)
                            total_building_price_usd = Decimal(total_building_price) * Decimal(sfl_price)
                            data_buildings.append([building_count, building, total_building_price_usd])
                            total_price += total_building_price
                            total_price_usd += total_building_price_usd
                        else:
                            continue

                    if data_buildings:
                        df_buildings = pd.DataFrame(data_buildings, columns=["Quantity", "Building", "Cost Price"])
                        df_buildings.set_index("Quantity", inplace=True)
                        df_buildings["Cost Price"] = pd.to_numeric(df_buildings["Cost Price"], errors="coerce")
                        df_buildings.sort_values(by="Cost Price", ascending=False, inplace=True)
                        df_buildings["Cost Price"] = "$" + df_buildings["Cost Price"].apply(lambda x: f"{x:.2f}")  
                        farm_worth_bui.write(df_buildings)
                    else:
                        farm_worth_bui.write("No buildings found.")
                    farm_worth_bui.success(f"📊 Total Cost Price: **${total_price_usd:.2f}**")

                farm_nft = {nft_buffs(inventory, return_type='total')}
                total_farm_nft = sum(farm_nft)
                total_farm_nft_usd = Decimal(str(total_farm_nft))

                #farm_worth_nft.info(" **This includes tradable NFT's that are currently withdrawables**")
                farm_worth_nft.write(nft_buffs(inventory, return_type='result_df'))
                farm_worth_nft.success(f"\n📊 Total Price: **${nft_buffs(inventory, return_type='total'):.2f}**")
                #farm_worth_decorative.info(" **This includes Flags (fixed $5), NFT's from Helios and also others non withdrawables**")        

                flag_items = {item: quantity for item, quantity in inventory_dict.items() if item.endswith("Flag")}
                nontradable_list = []

                flag_items = {item: quantity for item, quantity in inventory_dict.items() if item.endswith("Flag")}
                for item, quantity in flag_items.items():
                    price = 5.00 * int(quantity)
                    nontradable_list.append({'item': item, 'quantity': quantity, 'price': price})

                for item, quantity in inventory_dict.items():
                    if item in helios_sfl:
                        price = (helios_sfl[item] * int(quantity)) * (sfl_price)
                        nontradable_list.append({'item': item, 'quantity': quantity, 'price': price})

                for item, quantity in inventory_dict.items():
                    if item in nft_resources:
                        resources_nft = nft_resources[item]
                        price_nft = Decimal(0)
                        for resource, resource_quantity in resources_nft.items():
                            if resource == 'SFL':
                                price_nft += Decimal(resource_quantity)
                            elif resource in resources_items:
                                if resource == "Wood":
                                    price_nft += Decimal(resource_quantity) * Decimal(wood_price_converted)
                                elif resource == "Stone":
                                    price_nft += Decimal(resource_quantity) * Decimal(stone_price_converted)
                                elif resource == "Iron":
                                    price_nft += Decimal(resource_quantity) * Decimal(iron_price_converted)
                                elif resource == "Gold":
                                    price_nft += Decimal(resource_quantity) * Decimal(gold_price_converted)
                        price = price_nft * Decimal(quantity) * Decimal(sfl_price)
                        nontradable_list.append({'item': item, 'quantity': quantity, 'price': price})

                nontradable_dict = []

                for item in nontradable_list:
                    price = round(float(item['price']), 2)
                    nontradable_dict.append({'item': item['item'], 'quantity': item['quantity'], 'price': price})

                nontradable_df = pd.DataFrame(nontradable_dict, columns=['item', 'quantity', 'price'])
                nontradable_df = nontradable_df.rename(columns={'item': 'NFT', 'quantity': 'Quantity', 'price': 'Total Price'})
                nontradable_df = nontradable_df.sort_values(by='Total Price', ascending=False)
                nontradable_df = nontradable_df.reset_index(drop=True)
                nontradable_df = nontradable_df.set_index('NFT')
                nontradable_df['Total Price'] = nontradable_df['Total Price'].apply(lambda x: f'${x:.2f}')        
                total_price_sum = nontradable_df['Total Price'].str.replace('$', '', regex=False).astype(float).sum()

                farm_worth_decorative.write(nontradable_df)
                farm_worth_decorative.success(f"\n📊 Total Price: **${total_price_sum:.2f}**")

                # Create a dictionary of Average Price before removing the column       
                data_nft = nft_price()
                avg_price_dict = data_nft.to_dict('records')
                for i, dictionary in enumerate(avg_price_dict):
                    avg_price_dict[i] = {k: v for k, v in dictionary.items()}

                legacy_skill = {
                    "Liquidity Provider": 150.0,
                    "Artist": [item for item in avg_price_dict if item["NFT"] == "Apprentice Beaver"][0]["Average Price"],
                    "Coder": [item for item in avg_price_dict if item["NFT"] == "Scarecrow"][0]["Average Price"] * 3,
                    "Discord Mod": [item for item in avg_price_dict if item["NFT"] == "Apprentice Beaver"][0]["Average Price"],
                    "Logger": [item for item in avg_price_dict if item["NFT"] == "Apprentice Beaver"][0]["Average Price"] * 2,
                    "Lumberjack": [item for item in avg_price_dict if item["NFT"] == "Woody the Beaver"][0]["Average Price"] * 2,
                    "Gold Rush": [item for item in avg_price_dict if item["NFT"] == "Nugget"][0]["Average Price"] * 3,
                    "Prospector": [item for item in avg_price_dict if item["NFT"] == "Tunnel Mole"][0]["Average Price"] * 10,
                    "Wrangler": [item for item in avg_price_dict if item["NFT"] == "Speed Chicken"][0]["Average Price"],
                    "Barn Manager": [item for item in avg_price_dict if item["NFT"] == "Rich Chicken"][0]["Average Price"],
                    "Seed Specialist": [item for item in avg_price_dict if item["NFT"] == "Lunar Calendar"][0]["Average Price"],
                    "Green Thumb": 1.0
                }

                rows = []

                for item in inventory_dict.keys():
                    if item in legacy_skill:
                        skill_farm = legacy_skill[item]
                        nft = item
                        price = skill_farm

                        if isinstance(skill_farm, list):
                            nft = skill_farm[0]["NFT"]
                            if len(skill_farm) == 2:
                                price = skill_farm[0]["Average Price"] * skill_farm[1]
                            else:
                                price = skill_farm[0]["Average Price"]

                        rows.append([item, price])

                if not rows:
                    farm_worth_skill.error("This Farm doesn't have Legacy Skills")
                    skill_farm_total_usd = 0 
                else:
                    df_legacy_skills = pd.DataFrame(rows, columns=["Skill", "Price Estimate"])
                    skill_farm_total_usd = Decimal(df_legacy_skills["Price Estimate"].sum())
                    df_legacy_skills["Price Estimate"] = pd.to_numeric(df_legacy_skills["Price Estimate"], errors="coerce")
                    df_legacy_skills.sort_values(by="Price Estimate", ascending=False, inplace=True)
                    df_legacy_skills["Price Estimate"] = "$" + df_legacy_skills["Price Estimate"].apply(lambda x: f"{x:.2f}")                
                    df_legacy_skills.set_index("Skill", inplace=True)
                    farm_worth_skill.write(df_legacy_skills)
                    farm_worth_skill.success(f'📊 Total Estimate Value: **{skill_farm_total_usd:.2f}**')

                if bumpkin:
                    farm_worth_bump.info(f" #️⃣ **Bumpkin ID: #{bump_id}**")
                    farm_worth_bump.write(f"\n - 👖 Wearables Total Price: **${total_value_wearable:.2f}** \n - 📚 Levels Price Estimate: **${level_price:.2f}**") 
                    farm_worth_bump.write(f"\n") 
                    farm_worth_bump.success(f"\n 📊 Bumpkin Worth Estimate: **${bump_price_usd:.2f}**")
                else:
                    pass

                bbucks = (expansion_num - 3)
                bbucks_usd = bbucks * 0.1
                expansion_price_usd_bbucks = Decimal(str(expansion_price_usd)) + Decimal(str(bbucks_usd))
                total_price_sum_usd = Decimal(total_price_sum)
                balance_sfl_usd = Decimal(balance_sfl) * Decimal(sfl_price)
                farm_inv_sfl = Decimal(balance_sfl_usd) + Decimal(total_sales_usd)

                total_farm_usd = total_price_usd + expansion_price_usd_bbucks + total_sales_usd + total_farm_nft_usd + total_price_sum_usd + skill_farm_total_usd + balance_sfl_usd

                farm_worth.info(f"💰 Farm Inventory and SFL: **${farm_inv_sfl:.2f}**")
                farm_worth.success(f"🏡 **Farm Worth Estimate: ${total_farm_usd:.2f}**")
                if bumpkin:           
                    total_farm_bump_usd = Decimal(total_farm_usd) + Decimal(bump_price_usd)
                    farm_worth.warning(f"📊 **Estimate with Bumpkin: ${total_farm_bump_usd:.2f}**")
                else:
                    pass

                output = ""
                for resource, quantity in current_resources.items():
                    output += f"{resource} {quantity}, "
                output = output[:-2]
                farm_worth_exp.write(f" - 📋 **Resources used:** {output} and {bbucks} Block Bucks")

                farm_worth_exp.write("\n")
                farm_worth_exp.success(f"📊 Total Cost Price: **${expansion_price_usd_bbucks:.2f}**")

                farm_worth_how.info(f"The value of **Buildings, Expansions and Extras** are calculated using the **lowest listed price** for the required resources **at the Balloon**.")
                farm_worth_how.success(f"For **Tradables NFTs**, it uses the **average between the last sold price and the current lowest listing price on Opensea**, which is updated 1-2 times per day (semi-manually). And the **Extras** includes Flags (fixed $5), NFT's from Helios and also others non withdrawables")
                farm_worth_how.info(f"The **Legacy Skills** are calculated **pairing them with NFT's that have similar boost** and also considering their supply. Examples, **Seed Specialist = Lunar Calendar** or **Gold Rush = Nugget x 3**.")



            elif response.status_code == 429:
                status_ok.error("Error: Too many requests, please try again in a few seconds")
            elif response.status_code == 404:
                status_ok.error("Error 404: Make sure you are writing a valid Farm ID with only numbers")            
            else:
                status_ok.error(f"Error: {response.status_code}")
        else:
            pass
    except Exception as e:
        error_message = f"Error occurred in Farm {farm_id}: {str(e)}"
        sys.stderr.write(error_message)
        # Display the error message in Streamlit
        st.error(error_message)
     
with tab6:
    st.markdown("##### 🔻 SEARCH FARM ID 🔻")
    col_search, col_ok, buff = st.columns([2.5,2,6])
    with col_search:
        text_search = col_search.text_input("🔻 SEARCH FARM ID  🔻", label_visibility="collapsed", max_chars=6, value= FarmID)
    with col_ok:
        buttonok2 = col_ok.button('OK', key="OK2")        
        #st.error("The ranking is currently not working, it will be fixed soon™ ")
    col_rank, col_rank2, col_rank3, col_rank4 = st.columns([2,2,2,1.5])
    with col_rank:
        live_how = st.expander("📝 **HOW IT WORKS?**", expanded=False)
        live_ranking = st.expander("🎟️ **DAWN BREAKER TICKETS**", expanded=True)
        live_minted = st.expander("⚡ **DAWN BREAKER MINTS**", expanded=True)
        live_minted_error = st.container()   
        
    with col_rank2:
        live_update = st.container()        
        live_lantern = st.expander("🏮 **LANTERNS RANKING**", expanded=True) 
        live_odds = st.expander("🎲 **ODDS OF DIGGING**", expanded=True)
        
    with col_rank3:
        st.info(f"❤️ **Shoutout to Victor Gianvechio for providing the data.** ")
        live_treasure = st.expander("🐢 **TURTLES RACE**", expanded=True) 
        live_minted2 = st.expander("⚡ **TURTLES RACE MINTS**", expanded=True)
        
    with col_rank4:               
        live_mush = st.expander("🍄 **WILD MUSHROOM**", expanded=True)      
        live_calculator = st.expander("🤖 **LANTERNS CALCULATOR**", expanded=True)         

        

       
    from_lanterns = live_calculator.number_input("🔺 From How Many Lanters?", min_value=0, max_value=999, step=1)
    to_lanterns = live_calculator.number_input("🔻To How Many?", min_value=0, max_value=999, step=1, value=5)
    check_banner = live_calculator.checkbox("You have the Dawn Breaker Banner?", value=True, on_change=None,label_visibility="visible")
    buttonok4 = live_calculator.button('OK', key="OK4")  
    emojis_resources = emojis
    if buttonok4:
        try:
            lanterns_ing, lanterns_sfl = retrieve_lantern_ingredients()

            accumulated_lanterns_ing = {}
            accumulated_lanterns_sfl = 0.0

            if lanterns_sfl is not None:
                accumulated_lanterns_sfl = lanterns_sfl * (to_lanterns * (to_lanterns + 1) / 2)

            if from_lanterns > 0:
                from_lanterns_ing = {}
                from_lanterns_sfl = 0.0

                if lanterns_sfl is not None:
                    from_lanterns_sfl = lanterns_sfl * (from_lanterns * (from_lanterns + 1) / 2)

                for lantern_count in range(from_lanterns + 1):
                    for ingredient, quantity in lanterns_ing.items():
                        if ingredient not in from_lanterns_ing:
                            from_lanterns_ing[ingredient] = 0
                        from_lanterns_ing[ingredient] += int(quantity) * lantern_count

                accumulated_lanterns_ing = from_lanterns_ing
                extra_lanterns_sfl = accumulated_lanterns_sfl - from_lanterns_sfl
            else:
                extra_lanterns_sfl = accumulated_lanterns_sfl

            extra_lanterns_sfl_banner = extra_lanterns_sfl * 0.75
            extra_lanterns_ing = {}

            for ingredient, quantity in lanterns_ing.items():
                if ingredient == "Block Buck":
                    extra_quantity = to_lanterns - from_lanterns  # Fixed 1 per lantern
                else:
                    extra_quantity = int(quantity) * (to_lanterns * (to_lanterns + 1) / 2) - accumulated_lanterns_ing.get(ingredient, 0)
                extra_lanterns_ing[ingredient] = extra_quantity


            live_calculator.info(f"\n👨‍🏫 **Resources From {from_lanterns} to {to_lanterns} Lanterns:**")
            #live_calculator.write(f"- 💰 SFL: **{lanterns_ing}**")
            for ingredient, quantity in extra_lanterns_ing.items():
                live_calculator.write(f" - {emojis.get(ingredient)} {ingredient}: **{quantity:.0f}**")
            if lanterns_sfl is not None:
                if check_banner:                
                    live_calculator.write(f"- 💰 SFL: **{extra_lanterns_sfl_banner:.2f}**")
                else:
                    live_calculator.write(f"- 💰 SFL: **{extra_lanterns_sfl:.2f}**")
        except Exception as e:
            live_calculator.error(f"Error: {str(e)}")            
    
    live_how.info(f"📌 **This is using Dawn Breaker Tickets Dune query to get the TOP 10000 farms and then using the SFL API every 30~ min to refresh the info of the farms.**")
    live_how.info(f"⚠️ **Note that if your farm isn't in the TOP 10000 of the Dawn Breaker Tickets Dune query, is not going to show up in this Live Rankings.**") 

    first_respawn = 1682899200
    respawn_interval = timedelta(hours=16)

    current_time = datetime.now().timestamp()
    respawns = (current_time - first_respawn) // respawn_interval.total_seconds()
    next_respawn = datetime.fromtimestamp(first_respawn) + (respawns + 1) * respawn_interval

    time_remaining = next_respawn - datetime.fromtimestamp(current_time)
    hours_remaining = int(time_remaining.total_seconds() // 3600)
    minutes_remaining = int((time_remaining.total_seconds() % 3600) // 60)
    # Calculate the time and date of the next 50th respawn
    timestamp2 = 1685779200
    dt2 = datetime.fromtimestamp(timestamp2)

    time_remaining2 = dt2 - datetime.fromtimestamp(current_time)
    days_remaining2 = time_remaining2.days
    hours_remaining2 = time_remaining2.seconds // 3600
    minutes_remaining2 = (time_remaining2.seconds % 3600) // 60

    formatted_time_remaining = "{} Days {:02d}:{:02d} hours".format(days_remaining2, hours_remaining2, minutes_remaining2)
    
    live_mush.info("📊 **Total Respawns: {}**".format(int(respawns)))
    live_mush.success("⏭️ **Next Respawn in: {:02d}:{:02d} hours**".format(hours_remaining, minutes_remaining))
    #live_mush.warning("🚨 **50th Respawn in: {}**".format(formatted_time_remaining))
    #live_mush.markdown("##### 🍄 **WILD MUSHROOM RANKING**") 
    
    # Iterate over the list of queries and retrieve the owner counts     
    def create_dataframe():
        data = []
        for i, query_id in enumerate(queries):
            owner_count = fetch_owner_count(query_id)
            query_name = queries_name[i]
            query_emoji = queries_emoji[i]
            query_quantity = queries_quantity[i]
            query_ticket = queries_ticket[i]
            nft = f"{query_emoji} {query_name}"
            data.append([nft, owner_count, query_quantity, query_ticket])

        # Create a dataframe from the data list
        df_dune = pd.DataFrame(data, columns=["NFT", "Owners", "Supply", "Tickets"])
        return df_dune

    # Create or fetch the cached dataframe
    #@st.cache_data(ttl=30)
    def get_cached_dataframe():
        try:
            return create_dataframe()
        except Exception as e:
            st.error(f"Failed to fetch NFT mints. Error: {e}")
            return pd.DataFrame()

    df_dune = get_cached_dataframe()
    
    live_minted.info(f"👨‍🔬 **This info is from Dune**")
    # Display the dataframe
    live_minted.dataframe(df_dune, hide_index=True)           


    live_odds.info(f"📝 *Note: This data was calculated using the weight numbers in the Treasure Island Docs 06/06/2023 and the 1 in X are approximations.*")
    live_odds.write(f"- 🍾 Old Bottle: **5.19%** (1 in 19 with Shovels)")
    live_odds.write(f"- 🌿 Seaweed: **2.60%** (1 in 38 with Shovels)")
    live_odds.write(f"- 🧭 Iron Compasss: **0.52%** (1 in 192 with Shovels)")
    live_odds.write(f"- 🍾🌿 You **CAN'T** dig a Old Bottle/Seaweed with Drills")
    live_odds.write(f"- 🧭 Iron Compasss: **9.50%** (1 in 10 with Drills)")


        
    live_minted2.info(f" 🐢 **Emerald Turtle [0/100]**")
    live_minted2.write(f"- 🍾 **80** Old Bottles - 🌿 **50** Seaweed")
    live_minted2.write(f"- 🧭 **30** Iron Compass - 💰 **100** SFL")
    live_minted2.write("\n")
    live_minted2.success(f" 🥫 **Tin Turtle [0/3000]**")
    live_minted2.write(f"- 🍾 **50** Old Bottles - 🌿 **25** Seaweed")
    live_minted2.write(f"- 🧭 **15** Iron Compass - 💰 **40** SFL")
    
url_rank1 = 'http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking'
#url_rank2 = 'http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking' 

async def fetch(url, session):
    try:
        async with session.get(url, timeout=5) as response:
            return await response.json()
    except Exception as e:
        live_update.error("The ranking is currently not working, it will be fixed soon™ ")
        return None

async def main():
    try:
        async with aiohttp.ClientSession() as session:
            data1 = await fetch(url_rank1, session)        
            #data2 = await fetch(url_rank2, session)

        if data1 is not None:
            df1 = pd.DataFrame({
                'Farm': [farm['FarmID'] for farm in data1['farms']],
                'Tickets': [farm['DawnBreakerTicket'] if 'DawnBreakerTicket' in farm and farm['DawnBreakerTicket'] != '' else None for farm in data1['farms']],
                'Quest Done': [farm['Quest']['Completed'] if 'Completed' in farm['Quest'] else 0 for farm in data1['farms']],
                'Current Quest': [farm['Quest']['Description'] for farm in data1['farms']]
            })

            df2 = pd.DataFrame({
                'Farm': [farm['FarmID'] for farm in data1['farms']],
                'Week 10': [farm['LanternsCraftedByWeek']['10'] if 'LanternsCraftedByWeek' in farm and '10' in farm['LanternsCraftedByWeek'] else None for farm in data1['farms']],
                'Week 9': [farm['LanternsCraftedByWeek']['9'] if 'LanternsCraftedByWeek' in farm and '9' in farm['LanternsCraftedByWeek'] else None for farm in data1['farms']],       
                'Week 8': [farm['LanternsCraftedByWeek']['8'] if 'LanternsCraftedByWeek' in farm and '8' in farm['LanternsCraftedByWeek'] else None for farm in data1['farms']],
                'Week 7': [farm['LanternsCraftedByWeek']['7'] if 'LanternsCraftedByWeek' in farm and '7' in farm['LanternsCraftedByWeek'] else 0 for farm in data1['farms']],        
                'Week 6': [farm['LanternsCraftedByWeek']['6'] if 'LanternsCraftedByWeek' in farm and '6' in farm['LanternsCraftedByWeek'] else 0 for farm in data1['farms']],
                'Week 5': [farm['LanternsCraftedByWeek']['5'] if 'LanternsCraftedByWeek' in farm and '5' in farm['LanternsCraftedByWeek'] else 0 for farm in data1['farms']],        
                'Week 4': [farm['LanternsCraftedByWeek']['4'] if 'LanternsCraftedByWeek' in farm and '4' in farm['LanternsCraftedByWeek'] else 0 for farm in data1['farms']],
                'Week 3': [farm['LanternsCraftedByWeek']['3'] if 'LanternsCraftedByWeek' in farm and '3' in farm['LanternsCraftedByWeek'] else 0 for farm in data1['farms']],
                'Week 2': [farm['LanternsCraftedByWeek']['2'] if 'LanternsCraftedByWeek' in farm and '2' in farm['LanternsCraftedByWeek'] else 0 for farm in data1['farms']],
                'Week 1': [farm['LanternsCraftedByWeek']['1'] if 'LanternsCraftedByWeek' in farm and '1' in farm['LanternsCraftedByWeek'] else 0 for farm in data1['farms']]
            })

            df3 = pd.DataFrame({
                'Farm': [farm['FarmID'] for farm in data1['farms']],
                'Old Bottle': [farm['OldBottle'] if 'OldBottle' in farm and farm['OldBottle'] != '' else 0 for farm in data1['farms']],
                'Seaweed': [farm['Seaweed'] if 'Seaweed' in farm and farm['Seaweed'] != '' else 0 for farm in data1['farms']],
                'Iron Compass': [farm['IronCompass'] if 'IronCompass' in farm and farm['IronCompass'] != '' else 0 for farm in data1['farms']],
                'Davy Jones': ['YES' if int(farm.get('DavyJones', 0)) >= 1 else 'NO' for farm in data1['farms']]     
            })        


            # Remove rows with missing ticket counts
            df1 = df1.dropna(subset=['Tickets'])
            #df3 = df3.dropna(subset=['Wild Mushroom'])

            # MAKE SURE TOP 10 SHOWS
            top_ten_ids = fetch_top_ten_ids()
            lanterns_data = retrieve_lanterns_data(top_ten_ids)

            existing_ids = df2['Farm'].tolist()
            new_ids = []

            for farm_id in lanterns_data.keys():
                if farm_id not in existing_ids:
                    new_ids.append(farm_id)
                    lantern_data = lanterns_data[farm_id]
                    new_row = {
                        'Farm': farm_id,
                        'Week 8': lantern_data.get('8', None),
                        'Week 7': lantern_data.get('7', 0),
                        'Week 6': lantern_data.get('6', 0),
                        'Week 5': lantern_data.get('5', 0),
                        'Week 4': lantern_data.get('4', 0),
                        'Week 3': lantern_data.get('3', 0),
                        'Week 2': lantern_data.get('2', 0),
                        'Week 1': lantern_data.get('1', 0)
                    }
                    df2 = pd.concat([df2, pd.DataFrame(new_row, index=[0])], ignore_index=True)
            # Remove emphy columns
            df2 = df2.dropna(axis=1, how='all')


            # Convert Total Ticket column to numeric values
            df1['Tickets'] = pd.to_numeric(df1['Tickets'])
            df2['Week 7'] = pd.to_numeric(df2['Week 7'])
            df3['Old Bottle'] = pd.to_numeric(df3['Old Bottle'])
            df3['Seaweed'] = pd.to_numeric(df3['Seaweed'])
            df3['Iron Compass'] = pd.to_numeric(df3['Iron Compass'])

            # Sort by Total Ticket in descending order
            df1 = df1.sort_values(by='Tickets', ascending=False)
            df2 = df2.sort_values(by='Week 7', ascending=False)
            df3 = df3.sort_values(by=['Old Bottle', 'Iron Compass', 'Seaweed'], ascending=[False, False, False], kind='mergesort')


            df2 = df2.rename(columns={"Week 7": "Week 7 🔻"})   

            # Reset index and set the "Ranking" column as the new index
            df1 = df1.reset_index(drop=True)
            df2 = df2.reset_index(drop=True)
            df3 = df3.reset_index(drop=True)

            df1.index = df1.index + 1
            df2.index = df2.index + 1
            df3.index = df3.index + 1        

            # Rename the index to "Ranking"
            df1.index.name = "Rank"
            df2.index.name = "Rank"
            df3.index.name = "Rank"

            # Convert index to integer values
            df1.index = df1.index.astype(int)
            df2.index = df2.index.astype(int)
            df3.index = df3.index.astype(int)

            if df1.empty:
                live_update.error("The ranking is currently not working, it will be fixed soon™ ")
            else:
                live_update.success(f"🕘Updated at: **{datetime.strptime(data1['updatedAt'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M')} UTC**")

                if buttonok2:
                    df1 = df1.loc[df1['Farm'].str.contains(text_search)]
                    live_ranking.write(df1)
                    df2 = df2.loc[df2['Farm'].str.contains(text_search)]
                    live_lantern.write(df2)
                    df3 = df3.loc[df3['Farm'].str.contains(text_search)]
                    live_treasure.write(df3)   
                else: 
                    live_ranking.write(df1) 
                    live_lantern.write(df2)
                    live_treasure.write(df3)
            pass
    except Exception as e:
        live_update.error(f"The ranking is currently not working, it will be fixed soon™, Error: {str(e)}") 
    
if __name__ == "__main__":
    asyncio.run(main())   

with tab7:     
        status_ok2 = st.container() 
        col18, col19, col20, col21 = st.columns([2, 2, 2, 2], gap="medium")
        with col18:
            st.markdown("##### 🔻 SEARCH BUMPKIN ID 🔻")
            col_search2, col_ok2 = st.columns([2,2])
            with col_search2:
                text_search2 = col_search2.text_input("🔻 SEARCH BUMPKIN ID 🔻", label_visibility="collapsed", max_chars=5)
            with col_ok2:
                buttonok3 = col_ok2.button('OK', key="OK3")              
            bump_worth_how2 = st.expander("📝 **HOW IT WORKS?**", expanded=False) 
            bump_general2 = st.expander("📖 **GENERAL**", expanded=True)            
        with col19:            
            bump_info2 = st.expander("🖼️ PICTURE", expanded=True)
        with col20:
            bump_wearables2 = st.expander("👖 **WEARABLES**", expanded=True)
        with col21:
            bump_skill2 = st.expander("🏹 **SKILLS & ACHIEVEMENTS**", expanded=True)             
        
        if buttonok3:
            text_search2_strip = text_search2.strip()  # Get the value of text_search2 and remove leading/trailing spaces
            if text_search2_strip:  
                try:
                    text_search2_value = int(text_search2_strip)  # Convert to integer
                except ValueError:
                    status_ok2.error("Invalid Bumpkin ID. Please enter a valid numeric ID.")
                    sys.exit() # Stop execution if the ID is invalid                
                
                url2 = "https://api.sunflower-land.com/community/getBumpkins"
                payload2 = json.dumps({
                  "ids": [text_search2_value]
                })
                headers2 = {
                  'Content-Type': 'application/json'
                }            
                try:
                    response2 = requests.request("POST", url2, headers=headers2, data=payload2).json()
                except requests.exceptions.RequestException as e:
                    status_ok2.error("Error: Too many requests, please try again in a few seconds")
                    sys.exit()  # Stop execution if there is an API connection error            
                if "bumpkins" in response2:
                    bumpkins = response2["bumpkins"]
                    if str(text_search2_value) in bumpkins:
                        bumpkin2 = bumpkins[str(text_search2_value)]
                        if bumpkin2 == None:
                            status_ok2.error(f"The Bumpkin **{text_search2}** it isn't in the Bumpkins API, you can try to search it in this another site instead:")
                            status_ok2.markdown('🔗 <a href="https://sfl.shen.cyou/bumpkins" target="_blank">https://sfl.shen.cyou/bumpkins</a>', unsafe_allow_html=True)
                        else:
                            status_ok2.success(f" ✅ Done! Bumpkin **{text_search2_value}** loaded.")
                            bump_xp2 = bumpkin2.get("experience")
                            bump_id2 = bumpkin2.get("id")
                            bump_achi2 = bumpkin2.get("achievements")
                            bump_url2 = bumpkin2.get("tokenUri")           
                            skills_dict2 = {}
                            equipped_dict = {}

                            skills2 = bumpkin2.get("skills")
                            skills_dict = eval(str(skills2))
                            equipped2 = bumpkin2.get("equipped")
                            equipped_dict = eval(str(equipped2))

                            image_url2 = bump_url2.rfind("v1_")
                            if image_url2 != -1:
                                # Extract the substring after "v1_"
                                bump_url_last2 = bump_url2[image_url2 + len("v1_"):]
                                bump_img_url2 = f'<img src="https://images.bumpkins.io/nfts/{bump_url_last2}.png" width = 100%>'
                            else:
                                bump_img_url2 = ""

                            bump_general2.info(f" #️⃣ **Bumpkin ID: #{text_search2}**")

                            current_lvl2 = None
                            for level, info in xp_dict.items():
                                if bump_xp2 >= info['Total XP']:
                                    current_lvl2 = level

                            if current_lvl2 is None:
                                current_lvl2 = max(xp_dict.keys())

                            if current_lvl2 == max(xp_dict.keys()):
                                xp_needed2 = 'N/A'
                                nextlvl_xp2 = 'N/A'
                                extra_xp2 = 'N/A'
                            else:
                                if current_lvl2 in xp_dict:
                                    level_info2 = xp_dict[current_lvl2]
                                    xp_needed2 = level_info2['XP_next'] - (bump_xp2 - level_info2['Total XP'])
                                    nextlvl_xp2 = level_info2['XP_next']
                                    extra_xp2 = nextlvl_xp2 - xp_needed2
                                else:
                                    xp_needed2 = 'N/A'
                                    nextlvl_xp2 = 'N/A'
                                    extra_xp2 = 'N/A'

                            level_price2 = (bump_xp2 / 500) * sfl_price
                            # Check if the values are floats before rounding

                            filtered_df2 = wearable_list(equipped_dict, return_type='filtered_df')
                            total_value_wearable2 = wearable_list(equipped_dict, return_type='total')
                            bump_price_usd2 = total_value_wearable2 + level_price2

                            bump_info2.markdown(bump_img_url2, unsafe_allow_html=True)
                            bump_info2.write("\n")
                            bump_info2.success(f"\n📊 Total Worth Estimate: **${bump_price_usd2:.2f}**")

                            bump_worth_how2.info(
                                'The value of **Levels Price** are calculated using **500 XP = 1 SFL**, considering this kinda as average value cost of the most used meals XP and lowered a little bit to also **"value the time"**.')
                            bump_worth_how2.success(
                                'For **Bumpkin Wearables**, it uses the **average between the last sold price and the current lowest listing price on OpenSea**, which is updated 1-2 times per day (semi-manually).')

                            bump_general2.write(f" - 📗 Current Level: **{current_lvl2}**")
                            bump_general2.write(f" - 📘 Current Total XP: **{round(bump_xp2, 1)}**")
                            if current_lvl2 == max(xp_dict.keys()):
                                bump_general2.write(f" - 📙 Current Progress: **(MAX)**")
                                bump_general2.write(f" - ⏭️ XP for Next LVL: **(MAX)**")
                            else:
                                bump_general2.write(f" - 📙 Current Progress: **[{round(extra_xp2, 1)} / {nextlvl_xp2}]**")
                                bump_general2.write(f" - ⏭️ XP for Next LVL: **{round(xp_needed2, 1)}**")
                            bump_general2.write("\n")
                            bump_general2.success(f"\n📊 Levels Price Estimate: **${level_price2:.2f}**")

                            bump_wearables2.write(filtered_df2)
                            bump_wearables2.success(f"\n📊 Wearables Total Price: **${total_value_wearable2:.2f}**")

                            # Create lists to store the keys and descriptions
                            skill_names2 = []
                            skill_descriptions2 = []

                            # Iterate over the dictionary and extract the keys and descriptions
                            for key in skills_dict:
                                skill_names2.append(key)
                                skill_descriptions2.append(skills_description.get(key, "Description not available"))
                            # Create a DataFrame
                            df_skills2 = pd.DataFrame({"Skill": skill_names2, "Description": skill_descriptions2})
                            df_skills2.set_index("Skill", inplace=True)

                            # Write the DataFrame
                            bump_skill2.write(df_skills2)
                            bump_achi_total2 = len(bump_achi2)
                            bump_skill2.success(f"\n🏅 Total Achievements: **{bump_achi_total2}**")
                    else:
                        status_ok2.error(f"Bumpkin {text_search2} not found.")
                else:
                    status_ok2.error("Invalid response or error occurred.") 
with tab8:
    opensea_url_base = 'https://opensea.io/assets/matic/0x22d5f9b75c524fec1d6619787e582644cd4d7422/'
    opensea_url_bump = 'https://opensea.io/assets/matic/0x4bb5b2461e9ef782152c3a96698b2a4cf55b6162/'
    nft_list = {
        "crops": [
            {
                "name": "Peeled Potato",
                "type": ["🌱 Crop: #28a745","🥔 Potato: #c28669","🎲 Chance: #007bff"],
                "description": ["+20% chances of getting +1 Potato"],
                "currentPrice": 0,
                "url": "433",
                "urlImg": "https://i.seadn.io/gcs/files/15cba60fc1107e97163c09ce11af2aa7.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Cabbage Boy",
                "type": ["🌱 Crop: #28a745", "🌷 Cabbage: #e83e8c"],
                "description": ["+0.25 Cabbage Yield (+0.40 with Cabbage Girl)"],
                "combos": [{"name": "Cabbage Girl", "effect": "+0.15 cabbage", "buffs": True}],
                "currentPrice": 0,
                "url": "434",
                "urlImg": "https://i.seadn.io/gcs/files/584ee361c4adf52ffc6264b057fe3639.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Easter Bunny",
                "type": ["🌱 Crop: #28a745", "🥕 Carrot: #ff731c"],
                "description": ["+20% Carrot Yield"],
                "currentPrice": 0,
                "url": "909",
                "urlImg": "https://i.seadn.io/gcs/files/384aae3e5afad4cf5de9ff8f248f375c.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Pablo The Bunny",
                "type": ["🌱 Crop: #28a745", "🥕 Carrot: #ff731c"],
                "description": ["+0.1 Carrot Yield"],
                "currentPrice": 0,
                "url": "926",
                "urlImg": "https://i.seadn.io/gcs/files/f08eb724b62fed23fa962031e194e496.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },  
            {
                "name": "Victoria Sisters",
                "type": ["🌱 Crop: #28a745", "🎃 Pumpkin: #fd7e14"],
                "description": ["+20% Pumpkin Yield"],
                "currentPrice": 0,
                "url": "432",
                "urlImg": "https://i.seadn.io/gcs/files/1b594853ab0b5dee81c5c19fbaed79ab.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Maximus",
                "type": ["🌱 Crop: #28a745", "🍆 Eggplant: #6f42c1"],
                "description": ["+1 Eggplant Yield"],
                "currentPrice": 0,
                "url": "459",
                "urlImg": "https://i.seadn.io/gcs/files/222ef7e2b8595b68e3c84a01c15eaece.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },   
            {
                "name": "Obie",
                "type": ["🌱 Crop: #28a745", "🍆 Eggplant: #6f42c1", "⌛ Time: #dc3545"],
                "description": ["+25% Eggplant Grow Speed"],
                "currentPrice": 0,
                "url": "458",
                "urlImg": "https://i.seadn.io/gcs/files/d5a907b4f308788b3e1ef0dfa63ece74.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            }, 
            {
                "name": "Purple Trail",
                "type": ["🌱 Crop: #28a745", "🍆 Eggplant: #6f42c1"],
                "description": ["+0.2 Eggplant Yield"],
                "currentPrice": 0,
                "url": "457",
                "urlImg": "https://i.seadn.io/gcs/files/0fc9d7e55c80b72b1c252b88dc18b957.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },                 
            {
                "name": "Cabbage Girl",
                "type": ["🌱 Crop: #28a745", "🌷 Cabbage: #e83e8c", "⌛ Time: #dc3545"],
                "description": ["+50% Cabbage Grow Speed"],
                "combos": [{"name": "Cabbage Boy", "effect": "+0.15 cabbage"}],
                "currentPrice": 0,
                "url": "435",
                "urlImg": "https://i.seadn.io/gcs/files/c654499326ad0ef87512eccc2275120b.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Karkinos",
                "type": ["🌱 Crop: #28a745", "🌷 Cabbage: #e83e8c"],
                "description": ["+0.1 Cabbage Yield"],
                "info": "Has no effect with Cabbage Boy",
                "currentPrice": 0,
                "url": "455",
                "urlImg": "https://i.seadn.io/gcs/files/a2b12106880045dedf1bebcbf642a0f4.png?auto=format&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Mysterious Parsnip",
                "type": ["🌱 Crop: #28a745", "🤎 Parsnip: #c4914a", "⌛ Time: #dc3545"],
                "description": ["+50% Parsnip Grow Speed"],
                "currentPrice": 0,
                "url": "418",
                "urlImg": "https://i.seadn.io/gcs/files/a3807b9481c9549ab4c8b037f336cc48.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },           
            {
                "name": "Golden Cauliflower",
                "type": ["🌱 Crop: #28a745", "🤍 Cauliflower: #20c997"],
                "description": ["+200% Cauliflower Yield"],
                "currentPrice": 0,
                "url": "410",
                "urlImg": "https://i.seadn.io/gcs/files/b1940ac19227f809718204c092c6f1d8.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Carrot Sword",
                "type": ["🌱 Crop: #28a745", "🎲 Chance: #007bff"],
                "description": ["+300% Chances of Finding a Mutant Crop"],
                "currentPrice": 0,
                "url": "419",
                "urlImg": "https://i.seadn.io/gcs/files/ebe4db438955db4881651c2472c454f1.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Lunar Calendar",
                "type": ["🌱 Crop: #28a745", "⌛ Time: #dc3545"],
                "description": ["+10% Crops Grow Speed"],
                "currentPrice": 0,
                "url": "448",
                "urlImg": "https://i.seadn.io/gcs/files/b34ac337570367c010db967d594acd9d.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Nancy",
                "type": ["🌱 Crop: #28a745", "⌛ Time: #dc3545"],
                "description": ["+15% Crops Grow Speed"],
                "info": "Has no effect with Scarecrow and Kuebiko",
                "currentPrice": 0,
                "url": "420",
                "urlImg": "https://i.seadn.io/gcs/files/359e6d7eddd907318e1a9acfae922c80.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Scarecrow",
                "type": ["🌱 Crop: #28a745", "⌛ Time: #dc3545"],
                "description": ["+15% Crops Grow Speed | +20% Crop Yield"],
                "info": "Has no effect with Kuebiko",
                "currentPrice": 0,
                "url": "404",
                "urlImg": "https://i.seadn.io/gcs/files/5e507ea7b873600fbd7c94f25ebfdc4a.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Kuebiko",
                "type": ["🌱 Crop: #28a745", "⌛ Time: #dc3545"],
                "description": ["+15% Crops Grow Speed | +20% Crop Yield | Seeds are Free"],
                "currentPrice": 0,
                "url": "421",
                "urlImg": "https://i.seadn.io/gcs/files/50f0a2d783ddd177ab7fb616703b9107.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },           
            {
                "name": "Hoot",
                "type": ["🌱 Crop: #28a745", "🌾 Wheat: #eab412", "🥦 Kale: #016b18", "❤️ Radish: #c40000"],
                "description": ["+0.5 Yield for Wheat, Kale and Radish"],
                "currentPrice": 0,
                "url": "461",
                "urlImg": "https://i.seadn.io/gcs/files/526bb0ee4538efb1842cb5efe3d844b2.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Foliant",
                "type": ["🌱 Crop: #28a745", "🥦 Kale: #016b18"],
                "description": ["+0.2 Kale Yield"],
                "currentPrice": 0,
                "url": "1227",
                "urlImg": "https://i.seadn.io/gcs/files/f015f8235b5eca9a734624473858058d.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },            
            {
                "name": "Basic Scarecrow",
                "type": ["🌱 Crop: #28a745", "⌛ Time: #dc3545"],
                "description": ["+20% Grow Speed for Sunflowers, Potatos and Pumpkins"],
                "currentPrice": 0,
                "url": "462",
                "urlImg": "https://i.seadn.io/gcs/files/5a954084d82c27b8fdd6fa2cff9973c2.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": False,
            },
            {
                "name": "Sunflower Amulet",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🌻 Sunflower: #ffc107"],
                "description": ["+10% Sunflower Yield"],
                "currentPrice": 0,
                "url": "27",
                "urlImg": "https://i.seadn.io/gcs/files/f38c9c14b77c846acaeddfb6ba34f485.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },  
            {
                "name": "Carrot Amulet",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🥕 Carrot: #ff731c", "⌛ Time: #dc3545"],
                "description": ["+20% Carrot Grow Speed"],
                "currentPrice": 0,
                "url": "28",
                "urlImg": "https://i.seadn.io/gcs/files/7bcc04300bfc3fc7c7b7a73b0692ca0d.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },
            {
                "name": "Beetroot Amulet",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "💜 Beetroot: #6610f2"],
                "description": ["+20% Beetroot Yield"],
                "currentPrice": 0,
                "url": "29",
                "urlImg": "https://i.seadn.io/gcs/files/7e1a158e384cfd723076e9210ad638b4.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            }, 
            {
                "name": "Green Amulet",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🎲 Chance: #007bff"],
                "description": ["10% Chance of 10x Crops Yield"],
                "currentPrice": 0,
                "url": "30",
                "urlImg": "https://i.seadn.io/gcs/files/990e5aed14b88d868e42ec7b437bd450.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            }, 
            {
                "name": "Devil Wings",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🎲 Chance: #007bff"],
                "description": ["30% Chance of Harvesting Crops instantly"],
                "currentPrice": 0,
                "url": "72",
                "urlImg": "https://i.seadn.io/gcs/files/21de9ee9836f4b990857b0c65a0e3544.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },        
            {
                "name": "Angel Wings",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🎲 Chance: #007bff"],
                "description": ["30% Chance of Harvesting Crops instantly"],
                "currentPrice": 0,
                "url": "73",
                "urlImg": "https://i.seadn.io/gcs/files/c0e113852eb306dbfbf0243de79c5e4b.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },             
            {
                "name": "Sunflower Shield",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🌻 Sunflower: #ffc107"],
                "description": ["Free Sunflower Seeds"],
                "currentPrice": 0,
                "url": "31",
                "urlImg": "https://i.seadn.io/gcs/files/86dfc0cbc0d928526112529871a80643.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },  
            {
                "name": "Parsnip",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🤎 Parsnip: #c4914a"],
                "description": ["+20% Parsnip Yield"],
                "currentPrice": 0,
                "url": "56",
                "urlImg": "https://i.seadn.io/gcs/files/dd7d9ab5e04626e1fabc9ecaf7387871.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },              
            {
                "name": "Eggplant Onesie",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🌱 Crop: #28a745", "🍆 Eggplant: #6f42c1"],
                "description": ["+0.1 Eggplant Yield"],
                "currentPrice": 0,
                "url": "124",
                "urlImg": "https://i.seadn.io/gcs/files/fd74bc39605ed34dfb3d40fe5fd5681e.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },  
        ],
        "resources": [
            {
                "name": "Tiki Totem",
                "type": ["⚒️ Resources: #111111", "🌲 Wood: #9e6400"],
                "description": ["+0.1 Wood Drop"],
                "currentPrice": 0,
                "url": "447",
                "urlImg": "https://i.seadn.io/gcs/files/6d09b2a640a58f7f2669f0130c61e8ed.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Wood Nymph Wendy",
                "type": ["⚒️ Resources: #111111", "🌲 Wood: #9e6400"],
                "description": ["+0.2 Wood Drops"],
                "currentPrice": 0,
                "url": "436",
                "urlImg": "https://i.seadn.io/gcs/files/7eb82194c6db9590c91376a9822c257f.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Rock Golem",
                "type": ["⚒️ Resources: #111111", "⚪ Stone: #a5a5a5","🎲 Chance: #007bff"],
                "description": ["10% Chance to get +2 Stones"],
                "currentPrice": 0,
                "url": "427",
                "urlImg": "https://i.seadn.io/gcs/files/003cc83d6dae7a7526724ff33e2fd34f.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Iron Idol",
                "type": ["⚒️ Resources: #111111", "🟠 Iron: #d67c00"],
                "description": ["+1 Iron Drop"],
                "currentPrice": 0,
                "url": "454",
                "urlImg": "https://i.seadn.io/gcs/files/21292f5b71d879aa7f4359b2d0491b61.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Woody the Beaver",
                "type": ["⚒️ Resources: #111111", "🌲 Wood: #9e6400"],
                "description": ["+20% Increase Wood Drops"],
                "info": "Has no effect with Apprentice and Foreman",
                "currentPrice": 0,
                "url": "415",
                "urlImg": "https://i.seadn.io/gcs/files/8ec73be04115ac40bd984bc7542828da.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Apprentice Beaver",
                "type": ["⚒️ Resources: #111111", "🌲 Wood: #9e6400", "⌛ Time: #dc3545"],
                "description": ["+20% Increase Wood Drops | -50% Tree Recovery Time"],
                "info": "Has no effect with Foreman",
                "currentPrice": 0,
                "url": "416",
                "urlImg": "https://i.seadn.io/gcs/files/5101c63b5fc2afd06fe89838c31e902f.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Foreman Beaver",
                "type": ["⚒️ Resources: #111111", "🌲 Wood: #9e6400", "⌛ Time: #dc3545"],
                "description": ["+20% Increase Wood Drops | -50% Tree Recovery Time | Chop Trees without Axes"],                          
                "currentPrice": 0,
                "url": "417",
                "urlImg": "https://i.seadn.io/gcs/files/6784705d2180eaa375b4f4e5f85da2fb.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Tunnel Mole",
                "type": ["⚒️ Resources: #111111", "⚪ Stone: #a5a5a5"],
                "description": ["+25% Increase Stone Drops"],
                "currentPrice": 0,
                "url": "428",
                "urlImg": "https://i.seadn.io/gcs/files/81db80f91c6fa6e5e1cf1b88f0298a5d.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Rocky the Mole",
                "type": ["⚒️ Resources: #111111", "🟠 Iron: #d67c00"],
                "description": ["+25% Increase Iron Drops"],
                "currentPrice": 0,
                "url": "429",
                "urlImg": "https://i.seadn.io/gcs/files/a7a3bc576e532e98e698ee420103d43a.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Nugget",
                "type": ["⚒️ Resources: #111111", "🟡 Gold: #FFCC32"],
                "description": ["+25% Increase Gold Drops"],
                "currentPrice": 0,
                "url": "430",
                "urlImg": "https://i.seadn.io/gcs/files/a976a48605f56cdfec8fd5c682405a1d.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Tin Turtle",
                "type": ["⚒️ Resources: #111111", "⚪ Stone: #a5a5a5"],
                "description": ["+0.1 Stone in the Area of Effect (max 8 nodes)"],
                "currentPrice": 0,
                "url": "464",
                "urlImg": "https://raw.githubusercontent.com/sunflower-land/sunflower-land/ad9b557b2eea7715feeac10f19f643119842058b/public/erc1155/images/464.png",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Emerald Turtle",
                "type": ["⚒️ Resources: #111111", "⚪ Stone: #a5a5a5", "🟠 Iron: #d67c00", "🟡 Gold: #FFCC32"],
                "description": ["+0.5 Minerals in the Area of Effect (max 8 nodes)"],
                "currentPrice": 0,
                "url": "463",
                "urlImg": "https://raw.githubusercontent.com/sunflower-land/sunflower-land/ad9b557b2eea7715feeac10f19f643119842058b/public/erc1155/images/463.png",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },        
        ],
        
        "animals": [
            {
                "name": "Fat Chicken",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054"],
                "description": ["-10% Wheat requirement to feed Chickens"],
                "currentPrice": 0,
                "url": "611",
                "urlImg": "https://i.seadn.io/gcs/files/ce71d2650e1fb75d8adbf98f67472206.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Speed Chicken",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054"],
                "description": ["-10% Egg Production Time"],
                "currentPrice": 0,
                "url": "610",
                "urlImg": "https://i.seadn.io/gcs/files/41852d601b75e5b35eca2dc7c6bce57a.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Rich Chicken",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054"],
                "description": ["+0.1 Egg Yield"],
                "currentPrice": 0,
                "url": "612",
                "urlImg": "https://i.seadn.io/gcs/files/3695d80fbff44ea58a6f5d177774dc3d.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Ayam Cemani",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054"],
                "description": ["+0.2 Egg Yield"],
                "currentPrice": 0,
                "url": "445",
                "urlImg": "https://i.seadn.io/gcs/files/40e874b881858f943111a61fbbf41cbd.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Rooster",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054", "🎲 Chance: #007bff"],
                "description": ["2x Chances to get Mutant Chicken"],
                "currentPrice": 0,
                "url": "613",
                "urlImg": "https://i.seadn.io/gcs/files/e9affb424198c13fd1d5ec6a641ca12f.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Undead Rooster",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054"],
                "description": ["+0.1 Egg Yield"],
                "currentPrice": 0,
                "url": "1114",
                "urlImg": "https://i.seadn.io/gcs/files/6e935a1a2fc51b0ee7ffe69baeab6ae2.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Chicken Coop",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054"],
                "description": ["+1 Egg and +5 Chicken per Hen House"],
                "currentPrice": 0,
                "url": "408",
                "urlImg": "https://i.seadn.io/gcs/files/40135862a83c712a18b5fe35dec4a9c3.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Gold Egg",
                "type": ["🐔 Chicken: #bc2500", "🥚 Egg: #ffc054"],
                "description": ["Feed Chickens Without Wheat"],
                "currentPrice": 0,
                "url": "409",
                "urlImg": "https://i.seadn.io/gcs/files/5a9aff4a77cf16f8f2abee21e758c458.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
        ],
        "fruits": [
            {
                "name": "Lady Bug",
                "type": ["🍒 Fruit: #e83e8c", "🍎 Apple: #e80000"],
                "description": ["+0.25 Apple Drop"],
                "currentPrice": 0,
                "url": "442",
                "urlImg": "https://i.seadn.io/gcs/files/9efa739328da7f9bbb5f3b6f3826fe33.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Squirrel Monkey",
                "type": ["🍒 Fruit: #e83e8c", "🍊 Orange: #ffa719"],
                "description": ["-50% Orange Production Time"],
                "currentPrice": 0,
                "url": "443",
                "urlImg": "https://i.seadn.io/gcs/files/a9dad9cb12eb96261980d08b97249377.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Black Bearry",
                "type": ["🍒 Fruit: #e83e8c", "🍇 Blueberry: #2d05b2"],
                "description": ["+1 Blueberry Drop"],
                "currentPrice": 0,
                "url": "444",
                "urlImg": "https://i.seadn.io/gcs/files/8a22891f79abaf836310dc398b599d97.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Immortal Pear",
                "type": ["🍒 Fruit: #e83e8c"],
                "description": ["+1 Bonus Harvest"],
                "currentPrice": 0,
                "url": "441",
                "urlImg": "https://i.seadn.io/gcs/files/e62d63edf572779c4928034e983dc3ea.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": False,
            },
            {
                "name": "Fruit Picker Apron",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🍒 Fruit: #e83e8c"],
                "description": ["+0.1 Fruits Drop"],
                "currentPrice": 0,
                "url": "86",
                "urlImg": "https://i.seadn.io/gcs/files/605bd7471e40ce37bc6a395806670c29.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },  
        ],
        "xp": [
            {
                "name": "Maneki Neko",
                "type": ["🔼 Expirience: #3B88C3", "🎲 Chance: #007bff"],
                "description": ["+1 Random Food each 24 hours"],
                "currentPrice": 0,
                "url": "446",
                "urlImg": "https://i.seadn.io/gcs/files/eeadfc4c1c768af13739b4b3e9943ce8.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Observatory",
                "type": ["🔼 Expirience: #3B88C3"],
                "description": ["+5% Experience Boost"],
                "currentPrice": 0,
                "url": "911",
                "urlImg": "https://i.seadn.io/gcs/files/db470a7faa4948dad5d23ead2f2034bf.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Mushroom House",
                "type": ["🍄 Mushroom: #c13c6a"],
                "description": ["+0.2 Wild Mushrooms Drop"],
                "currentPrice": 0,
                "url": "456",
                "urlImg": "https://i.seadn.io/gcs/files/cbf74b26df2f03e2faf5bb39c15edb9d.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Christmas Tree",
                "type": ["🎲 Chance: #007bff"],
                "description": ["+1 Mysterious drop at Christmas Eve (Last drop: Devil/Angel Wings)"],
                "currentPrice": 0,
                "url": "403",
                "urlImg": "https://i.seadn.io/gcs/files/036e41b320664fb3d6e6502b30ff3ca8.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Golden Spatula",
                "type": ["👨‍🌾 Bumpkin: #e04a83","🔼 Expirience: #3B88C3"],
                "description": ["+10% Experience Boost"],
                "currentPrice": 0,
                "url": "58",
                "urlImg": "https://i.seadn.io/gcs/files/97a774bf000b26efb31e1dedd9a674aa.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },
            {
                "name": "Chef Apron",
                "type": ["👨‍🌾 Bumpkin: #e04a83","💸 SFL: #f4b811"],
                "description": ["+20% Profit from Selling Cakes"],
                "currentPrice": 0,
                "url": "16",
                "urlImg": "https://i.seadn.io/gcs/files/ffba3d642bf8cff7e5cb5309d471b31b.png?auto=format&dpr=1&w=384",
                "collection": "Bumpkin",
                "isSelling": True,
            },  
        ],
        "treasure": [
            {
                "name": "Heart of Davy Jones",
                "type": ["🏝️ Treasure Island: #c19a2e"],
                "description": ["+20 Digs Amount in Treasure Island (Total 50)"],
                "currentPrice": 0,
                "url": "450",
                "urlImg": "https://i.seadn.io/gcs/files/6b4ddc31bbe8e1c21fecfaf383307352.gif?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Genie Lamp",
                "type": ["🏝️ Treasure Island: #c19a2e", "🎲 Chance: #007bff"],
                "description": ["Grants 3 Random Wishes"],
                "currentPrice": 0,
                "url": "460",
                "urlImg": "https://i.seadn.io/gcs/files/e34f1abb9f095d8511551389d37062af.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": True,
            },
            {
                "name": "Treasure Map",
                "type": ["🏝️ Treasure Island: #c19a2e", "💸 SFL: #f4b811"],
                "description": ["+20% Profit from Beach Bounty Items"],
                "currentPrice": 0,
                "url": "449",
                "urlImg": "https://i.seadn.io/gcs/files/ed79724f8711e7a1f4db4cf2a4deddba.png?auto=format&dpr=1&w=384",
                "collection": "Sunflower Land Collectibles",
                "isSelling": False,
            },            
        ],
    }

    col_nft, how_nft = st.columns([2,2])
    with col_nft:        
        keywords = st_tags(
            label='🔻 **SEARCH WITH TAGS:** 🔻',
            text='Press enter to add more',
            #value=['Crop'],
            suggestions=['Peeled','Potato','Treasure','Fruit','Mushroom','SFL','Sunflower','Bumpkin','Egg','Chicken','Expirience','Apple','Orange','Blueberry','Crop','Cabbage','Boy','Girl','Easter','Bunny','Carrot','Pablo','Victoria','Sisters','Pumpkin','Maximus','Eggplant','Obie','Purple','Trail','Karkinos','Mysterious','Parsnip','Golden','Cauliflower','Sword','Lunar','Calendar','Nancy','Scarecrow','Kuebiko','Hoot','Foliant','Basic','Tiki','Totem','Wood','Nymph','Wendy','Rock','Golem','Stone','Chance'],
            maxtags=4,
            key="tags"
        )
    #with col_nft2:
    #    nft_collec = st.multiselect(
    #        'From witch Collections?',
    #        ['Sunflower Land', 'Bumpkins Wearables'],
    #        ['Sunflower Land', 'Bumpkins Wearables'])
    with how_nft:
        st.write("\n")  
        st.write("\n") 
        how_nft = st.expander("📝 **HOW IT WORKS?**", expanded=False) 
     
    how_nft.info(f"The value of **NFT's from the Sunflower Land Collection**, it calculated using the **average between the last sold price and the current lowest listing price on Opensea**, which is updated 1-2 times per day (semi-manually).")
    how_nft.success(f"For **Bumpkins Wearables**, it is using a similar method with only difference that is not the average price, it is just the **last sold price in OpenSea.**")
    how_nft.info(f"About the NFT's that say **Still Not Tradable** it means that they are going to be tradable in the future but at the moment you can't withdraw them and the **Not for Sale** ones they are never going to be tradable.")


    def populate_tags_dict(data):
        tags_dict = {}

        for item_category in data.values():
            for item in item_category:
                types = item.get("type", [])  # Get the type list for the item

                for type_str in types:
                    type_name = (
                        type_str.split(":")[0].strip()
                        if ":" in type_str
                        else type_str.strip()
                    )  # Extract the type name

                    # Add the type name to the tags_dict
                    if type_name not in tags_dict:
                        tags_dict[type_name] = []

                    tags_dict[type_name].append(item["name"])

        return tags_dict
    

    async def display_nft_cards_async(nft_list, column1, column2, column3, column4):
        index = 0  # Initialize index outside the loop

        for item in nft_list:
            # Generate type badges with colors
            type_badges = " ".join([
                f'<span class="badge text-center rounded-pill start-50" style="font-size:1rem;background-color:{t.split(":")[1].strip()}">{t.split(":")[0].strip()}</span>'
                if ":" in t
                else f'<span class="badge text-center rounded-pill start-50" style="font-size:1rem;">{t.strip()}</span>'
                for t in item["type"]
            ])
            

            if item["collection"] == "Sunflower Land Collectibles":
                opensea_link = opensea_url_base
                current_price = nft_price(item["name"], return_type='nft_list')
                current_price_html = f'💰 Avg Price: ${current_price}'
            else:
                opensea_link = opensea_url_bump
                current_price = wearable_price(item["name"], return_type='nft_list')       
                current_price_html = f'💰 Last Sale: ${current_price}'

            if current_price is None:
                if item["isSelling"] is False:
                    current_price_html = '❌ Not For Sale'
                else:
                    current_price_html = '❌ Still Not Tradable'
            
            info_alert = item.get("info")
            if info_alert is None:
                info_alert_html = f"&nbsp;"
            else:
                info_alert_html = f'<span class="card-text" style="color:#ffc107;">🚨 <b>{info_alert}</b></span>'

            markdown_content = """
            <div class="card rounded border-top border-5 border-dark text-white bg-dark mb-5 h-100" style="max-width: 25rem;">            
                <a href="{}{}" style="display: inline-block" target="_blank">
                    <img src="{}" alt="NFT Image" class="card-img-top rounded-top rounded-3"></a>
                <button type="button" class="position-absolute top-0 start-0 mt-2 ml-2 btn btn-sm btn-secondary d-none d-md-block" style="width: 3rem; height:2.2rem;opacity:0.75;"><h6><b>#{}</b></h6></button>
                <div class="w-100 p-2 bg-secondary position-relative bottom-0 text-center">
                    {}
                </div>                 
                <div class="card-body" style="min-height:8rem">
                    <h5 class="card-title" style="padding-bottom:0rem;">🏷️ <b>{}</b></h5>
                    <span class="card-text">📖 <b>Description: </b>{}</span></span>
                    {}
                </div>
                <div class="card-footer">
                    <span class="card-text"><b>{}</b></span>                     
                </div>
            </div>
            """.format(
                opensea_link,
                item["url"],
                item["urlImg"],
                index +1,
                type_badges,
                item["name"],
                item["description"][0],
                info_alert_html,
                current_price_html,
                item["collection"],
            )

            if index % 4 == 0:
                column1.markdown(markdown_content, unsafe_allow_html=True)
            elif index % 4 == 1:
                column2.markdown(markdown_content, unsafe_allow_html=True)
            elif index % 4 == 2:
                column3.markdown(markdown_content, unsafe_allow_html=True)
            else:
                column4.markdown(markdown_content, unsafe_allow_html=True)

            index += 1  # Increment index inside the loop 
    
    tags_dict = populate_tags_dict(nft_list)

    selected_tags = set(tag.lower() for tag in keywords)  # Convert selected_tags to lowercase
    
    async def main2():
        # Filter items based on selected tags
        filtered_items = []
        if not selected_tags:  # If no tags are selected, display all items
            for item_category in nft_list.values():
                filtered_items.extend(item_category)
        else:
            for item_category in nft_list.values():
                for item in item_category:
                    types = item.get("type", [])
                    for tag in selected_tags:
                        if any(tag.lower() in type.lower() for type in types):
                            filtered_items.append(item)
                            break
                    else:
                        # Check similarity between tag and item name
                        name = item.get("name", "").lower()
                        for tag in selected_tags:
                            similarity_ratio = fuzz.partial_ratio(tag.lower(), name)
                            if similarity_ratio >= 85:  # Adjust the threshold as needed
                                filtered_items.append(item)
                                break
        # Create the layout grid for the item cards
        colA, colB, colC, colD = tab8.columns([3, 3, 3, 3])
        with colA:
            column1 = st.container()
        with colB:
            column2 = st.container()
        with colC:
            column3 = st.container()
        with colD:
            column4 = st.container()

        await display_nft_cards_async(filtered_items, column1, column2, column3, column4)

# Run the async function
    if __name__ == "__main__":
        asyncio.run(main2())
# Call the function with filtered_items
#    display_nft_cards(filtered_items)
