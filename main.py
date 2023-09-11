import asyncio
import json
from typing import Any

import aiohttp
import streamlit as st
from PIL import Image
from streamlit.delta_generator import DeltaGenerator

from priceapi import PriceAPI
from tabs.bumpkin import BumpkinTab
from tabs.home import HomeTab
from tabs.ranking import RankingTab
from tabs.top import TopTab

# if TYPE_CHECKING:
#     from pandas import Series
favicon: Any = Image.open("favicon.png")
st.set_page_config(
    page_title="SFL Plus",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)


# st.write(
#     '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/
# bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1a
# oWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm"
# crossorigin="anonymous">',
#     unsafe_allow_html=True,
# )
def local_css(file_name) -> None:
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


class Main:
    def __init__(self) -> None:
        self.version = "v4.0"
        self.priceAPI: PriceAPI = PriceAPI()
        local_css("style.css")
        self.eth_price: float = self.priceAPI.retrieve_eth_price()
        self.matic_price: float = self.priceAPI.retrieve_matic_price()
        self.sfl_price: float = self.priceAPI.retrieve_sfl_price()
        self.sfl_supply: int | None = self.priceAPI.get_token_supply()
        app_state_temp: dict[
            str, list[str]
        ] = st.experimental_get_query_params()

        # fetch the first item in each query string as we don't have multiple
        # values for each query string key in this example
        self.app_state: dict[str, str] = {
            k: v[0] if isinstance(v, list) else v
            for k, v in app_state_temp.items()
        }
        with open("data/skill_descriptions.json", "r", encoding="utf-8") as f:
            self.skills_description: dict[str, str] = json.load(f)
        with open("data/xp_data.json", "r", encoding="utf-8") as f:
            self.xp_dict: dict[int, dict[str, int | None]] = {
                int(k): v for k, v in json.load(f).items()
            }
        with open("data/wearables_sfl.json", "r", encoding="utf-8") as f:
            self.wearables_sfl: dict[str, int] = json.load(f)
        with open("data/inventory_items.json", "r", encoding="utf-8") as f:
            self.inventory_items: list[str] = json.load(f)
        with open("data/emojis.json", "r", encoding="utf-8") as f:
            self.emojis: dict[str, str] = json.load(f)
        with open("data/limits.json", "r", encoding="utf-8") as f:
            self.limits: dict[str, int] = json.load(f)
        self.fruits: list[str] = ["Apple", "Orange", "Blueberry"]
        self.fruits_price: dict[str, float] = {
            "Apple": 0.15625,
            "Orange": 0.1125,
            "Blueberry": 0.075,
        }
        self.fruit_emojis: dict[str, str] = {
            "Apple": " 🍎 ",
            "Orange": " 🍊 ",
            "Blueberry": " 🍇 ",
        }
        TopTab(self)
        tab1: DeltaGenerator
        tab2: DeltaGenerator
        tab3: DeltaGenerator
        tab1, tab2, tab3 = st.tabs(
            ["💾HOME", "🏆RANKING", "👥BUMPKIN"]
        )  # "📜NFT LIST", "👨‍🔬CALCULATOR", "💸TRADER"
        # Define default farm ID
        hometab = HomeTab(self, tab1)
        self.farm_id: str = hometab.get_farm_id()
        hometab.get_containers()
        ranktab = RankingTab(self, tab2)
        self.rank_tab_cons: dict[str, DeltaGenerator] = ranktab.get_containers()
        BumpkinTab(self, tab3)


url_rank1 = "http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking"


async def fetch(url, session: aiohttp.ClientSession) -> dict:
    async with session.get(url, timeout=5) as response:
        return await response.json()


async def main() -> None:
    Main()


if __name__ == "__main__":
    asyncio.run(main())


footer = """<style>
a:link , a:visited{
    color:rgba(250, 250, 250, 0.9);
    text-decoration: underline;
}

a:hover,  a:active {
    color:rgba(250, 250, 250, 1);
    text-decoration: underline;
}
.footer {
    background: rgb(14, 17, 23);
    color: rgba(250, 250, 250, 0.7);
    padding-top: 0.5rem;
    z-index: 1;
}
@media screen and (min-width: 768px) {
    .footer {
        position: fixed;
        bottom: -0.5rem;
        left: 0;
        padding-left:5rem;
        padding-right:5rem;
        width: 100%;
    }
}
@media screen and (max-width: 767px) {
    .footer {
        position: relative;
    }
}

</style>
<div class="footer">
<p style="font-size: 0.9rem;">Live Trade Prices Powered 💚 by
    <b><a href="https://sfl.tools/" target="_blank">sfl.tools</a></b>
</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
