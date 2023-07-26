from typing import TYPE_CHECKING
import streamlit as st
import requests
from decimal import Decimal

DS_BASE_URL = "https://api.dexscreener.com/latest/dex/pairs"
CG_BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

COINGECKO_SFL_URL: str = f"{CG_BASE_URL}?ids=sunflower-land&vs_currencies=usd"
COINGECKO_MATIC_URL: str = f"{CG_BASE_URL}?ids=matic-network&vs_currencies=usd"
COINGECKO_ETH_URL: str = f"{CG_BASE_URL}?ids=ethereum&vs_currencies=usd"

DEXSCREENER_SFL_URL: str = (
    f"{DS_BASE_URL}/polygon/0x6f9E92DD4734c168A734B873dC3db77E39552eb6"
)
DEXSCREENER_MATIC_URL: str = (
    f"{DS_BASE_URL}/ethereum/0x290a6a7460b308ee3f19023d2d00de604bcf5b42"
)
DEXSCREENER_ETH_URL: str = (
    f"{DS_BASE_URL}/bsc/0x63b30de1a998e9e64fd58a21f68d323b9bcd8f85"
)

SFL_CONTRACT = "0xd1f9c58e33933a993a3891f8acfe05a68e1afc05"
POLYGONSCAN_API_KEY = "QJKGEWQQI8UQSZQDMQQPYJU8Q7D5CCDSQV"
SUPPLY_URL: str = (
    f"https://api.polygonscan.com/api?module=stats"
    + f"&action=tokensupply&contractaddress={SFL_CONTRACT}"
    + f"&apikey={POLYGONSCAN_API_KEY}"
)

if TYPE_CHECKING:
    from requests import Response


class PriceAPI:
    @st.cache_resource(
        ttl=600, show_spinner="Updating the Resources Prices"
    )  # cache for 10 min
    def get_resource_price(_self, resource_id) -> Decimal:
        url = "https://sfl.tools/api/listings/prices"
        response = requests.get(url).json()
        if str(resource_id) in response:
            price = response[str(resource_id)]["pricePerUnitTaxed"]
            return Decimal(price)
        else:
            raise Exception("Failed to get resource price.")

    @st.cache_resource(
        ttl=3600, show_spinner="Updating the SFL Supply"
    )  # cache for 1 hour
    def get_token_supply(_self) -> int | None:
        try:
            response: Response = requests.get(SUPPLY_URL)
            if response.status_code != 200:
                raise Exception("Failed to get SFL Supply.")
            supply = response.json()["result"]
            return int(supply)
        except Exception:
            return None

    def get_eth_price_ds(_self) -> float:
        response: Response = requests.get(DEXSCREENER_ETH_URL)
        if response.status_code != 200:
            raise Exception("Failed to get ETH price from Dexscreener API.")
        eth_price = response.json()["pairs"][0]["priceUsd"]
        try:
            price = float(eth_price)
            return price
        except ValueError as e:
            raise Exception("Failed to get ETH price from Dexscreener API.")

    def get_eth_price_cg(_self) -> float:
        eth_response: Response = requests.get(COINGECKO_ETH_URL)
        if eth_response.status_code != 200:
            raise Exception("Failed to get Ethereum price from Coingecko API.")
        eth_price: float = eth_response.json()["ethereum"]["usd"]
        return eth_price

    def get_matic_price_ds(_self) -> float:
        response: Response = requests.get(DEXSCREENER_MATIC_URL)
        if response.status_code != 200:
            raise Exception("Failed to get Matic price from Dexscreener API.")
        matic_price: str = response.json()["pairs"][0]["priceUsd"]
        try:
            price = float(matic_price)
            return price
        except ValueError as e:
            raise Exception("Failed to get Matic price from Dexscreener API.")

    def get_matic_price_cg(_self) -> float:
        matic_response: Response = requests.get(COINGECKO_MATIC_URL)
        if matic_response.status_code != 200:
            raise Exception("Failed to get Matic price from Coingecko API.")
        matic_price: float = matic_response.json()["matic-network"]["usd"]
        return matic_price

    def get_sfl_price_ds(_self) -> float:
        response: Response = requests.get(DEXSCREENER_SFL_URL)
        if response.status_code != 200:
            raise Exception("Failed to get SFL price from Dexscreener API.")
        sfl_price = response.json()["pairs"][0]["priceUsd"]
        try:
            price = float(sfl_price)
            return price
        except ValueError as e:
            raise Exception("Failed to get SFL price from Dexscreener API.")

    def get_sfl_price_cg(_self) -> float:
        sfl_response: Response = requests.get(COINGECKO_SFL_URL)
        if sfl_response.status_code != 200:
            raise Exception("Failed to get SFL price from Coingecko API.")
        sfl_price: float = sfl_response.json()["sunflower-land"]["usd"]
        return sfl_price

    @st.cache_resource(
        ttl=3600, show_spinner="Updating the ETH Price"
    )  # cache for 1 hour
    def retrieve_eth_price(_self) -> float:
        eth_price: float = _self.get_eth_price_ds()
        if eth_price is None:
            eth_price: float = _self.get_eth_price_cg()
            if eth_price is None:
                raise Exception(
                    "Failed to retrieve Ethereum price from both Coingecko "
                    + "and Dexscreener APIs. Please try again later."
                )
        return eth_price

    @st.cache_resource(
        ttl=3600, show_spinner="Updating the Matic Price"
    )  # cache for 1 hour
    def retrieve_matic_price(_self):
        matic_price: float = _self.get_matic_price_ds()
        if matic_price is None:
            matic_price = _self.get_matic_price_cg()
            if matic_price is None:
                raise Exception(
                    "Failed to retrieve Matic price from both Coingecko "
                    + "and Dexscreener APIs. Please try again later."
                )
        return matic_price

    @st.cache_resource(
        ttl=3600, show_spinner="Updating the SFL Price"
    )  # cache for 1 hour
    def retrieve_sfl_price(_self) -> float:
        sfl_price: float = _self.get_sfl_price_ds()
        if sfl_price is None:
            sfl_price = _self.get_sfl_price_cg()
            if sfl_price is None:
                raise Exception(
                    "Failed to retrieve SFL price from both Coingecko "
                    + "and Dexscreener APIs. Please try again later."
                )
        return sfl_price
