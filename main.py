from typing import TYPE_CHECKING, Any
import json
from PIL import Image
import pandas as pd
from pandas import DataFrame
import asyncio
import aiohttp
from datetime import datetime

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from priceapi import PriceAPI
from tabs.home import HomeTab
from tabs.top import TopTab
from tabs.bumpkin import BumpkinTab
from tabs.ranking import RankingTab

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
        self.version = "v3.2"
        self.priceAPI: PriceAPI = PriceAPI()
        local_css("style.css")

        self.eth_price: float = self.priceAPI.retrieve_eth_price()
        self.matic_price: float = self.priceAPI.retrieve_matic_price()
        self.sfl_price: float = self.priceAPI.retrieve_sfl_price()

        self.sfl_supply: int | None = self.priceAPI.get_token_supply()

        self.API_KEY_DUNE = "xEB9BjuGBc5SbpVABb2VHcVV5DQ1g3K2"

        self.queries_owners: list[Any] = [100, None, None]
        self.queries: list[str] = ["2649121", "2649118", "2427499"]  #
        self.queries_name: list[str] = [
            "Emerald Turtle",
            "Tin Turtle",
            "Purple Trail",
        ]  #
        self.queries_quantity: list[str] = [
            "100 (SOLD OUT)",
            "3000",
            "10000",
        ]  #
        self.queries_emoji: list[str] = ["🐢", "🥫", "🐌"]  #
        # queries_ticket = ["3200", "1200", "500"]

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
        farm_tab_cons: dict[str, DeltaGenerator] = hometab.get_containers()

        ranktab = RankingTab(self, tab2)
        self.rank_tab_cons: dict[str, DeltaGenerator] = ranktab.get_containers()
        bumpkintab = BumpkinTab(self, tab3)


url_rank1 = "http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking"
# url_rank2 = 'http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking'


async def fetch(url, session: aiohttp.ClientSession) -> dict:
    async with session.get(url, timeout=5) as response:
        return await response.json()


async def main() -> None:
    main_app = Main()
    try:
        async with aiohttp.ClientSession() as session:
            try:
                data1 = await fetch(url_rank1, session)
            except Exception as e:
                main_app.rank_tab_cons["live_update"].error(
                    "The ranking is currently not working, will be fixed soon™"
                )
                return
            # data2 = await fetch(url_rank2, session)

        df1 = pd.DataFrame(
            {
                "Farm": [farm["FarmID"] for farm in data1["farms"]],
                "Tickets": [
                    farm["DawnBreakerTicket"]
                    if "DawnBreakerTicket" in farm
                    and farm["DawnBreakerTicket"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Quest Done": [
                    farm["Quest"]["Completed"]
                    if "Completed" in farm["Quest"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Current Quest": [
                    farm["Quest"]["Description"] for farm in data1["farms"]
                ],
            }
        )

        df2 = pd.DataFrame(
            {
                "Farm": [farm["FarmID"] for farm in data1["farms"]],
                "Week 10": [
                    farm["LanternsCraftedByWeek"]["10"]
                    if "LanternsCraftedByWeek" in farm
                    and "10" in farm["LanternsCraftedByWeek"]
                    else None
                    for farm in data1["farms"]
                ],
                "Week 9": [
                    farm["LanternsCraftedByWeek"]["9"]
                    if "LanternsCraftedByWeek" in farm
                    and "9" in farm["LanternsCraftedByWeek"]
                    else None
                    for farm in data1["farms"]
                ],
                "Week 8": [
                    farm["LanternsCraftedByWeek"]["8"]
                    if "LanternsCraftedByWeek" in farm
                    and "8" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 7": [
                    farm["LanternsCraftedByWeek"]["7"]
                    if "LanternsCraftedByWeek" in farm
                    and "7" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 6": [
                    farm["LanternsCraftedByWeek"]["6"]
                    if "LanternsCraftedByWeek" in farm
                    and "6" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 5": [
                    farm["LanternsCraftedByWeek"]["5"]
                    if "LanternsCraftedByWeek" in farm
                    and "5" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 4": [
                    farm["LanternsCraftedByWeek"]["4"]
                    if "LanternsCraftedByWeek" in farm
                    and "4" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 3": [
                    farm["LanternsCraftedByWeek"]["3"]
                    if "LanternsCraftedByWeek" in farm
                    and "3" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 2": [
                    farm["LanternsCraftedByWeek"]["2"]
                    if "LanternsCraftedByWeek" in farm
                    and "2" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 1": [
                    farm["LanternsCraftedByWeek"]["1"]
                    if "LanternsCraftedByWeek" in farm
                    and "1" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
            }
        )

        df2 = pd.DataFrame(
            {
                "Farm": [farm["FarmID"] for farm in data1["farms"]],
                "Week 10": [
                    farm["LanternsCraftedByWeek"]["10"]
                    if "LanternsCraftedByWeek" in farm
                    and "10" in farm["LanternsCraftedByWeek"]
                    else None
                    for farm in data1["farms"]
                ],
                "Week 9": [
                    farm["LanternsCraftedByWeek"]["9"]
                    if "LanternsCraftedByWeek" in farm
                    and "9" in farm["LanternsCraftedByWeek"]
                    else None
                    for farm in data1["farms"]
                ],
                "Week 8": [
                    farm["LanternsCraftedByWeek"]["8"]
                    if "LanternsCraftedByWeek" in farm
                    and "8" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 7": [
                    farm["LanternsCraftedByWeek"]["7"]
                    if "LanternsCraftedByWeek" in farm
                    and "7" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 6": [
                    farm["LanternsCraftedByWeek"]["6"]
                    if "LanternsCraftedByWeek" in farm
                    and "6" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 5": [
                    farm["LanternsCraftedByWeek"]["5"]
                    if "LanternsCraftedByWeek" in farm
                    and "5" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 4": [
                    farm["LanternsCraftedByWeek"]["4"]
                    if "LanternsCraftedByWeek" in farm
                    and "4" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 3": [
                    farm["LanternsCraftedByWeek"]["3"]
                    if "LanternsCraftedByWeek" in farm
                    and "3" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 2": [
                    farm["LanternsCraftedByWeek"]["2"]
                    if "LanternsCraftedByWeek" in farm
                    and "2" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
                "Week 1": [
                    farm["LanternsCraftedByWeek"]["1"]
                    if "LanternsCraftedByWeek" in farm
                    and "1" in farm["LanternsCraftedByWeek"]
                    else 0
                    for farm in data1["farms"]
                ],
            }
        )

        df3 = pd.DataFrame(
            {
                "Farm": [farm["FarmID"] for farm in data1["farms"]],
                "Bottles": [
                    farm["OldBottle"]
                    if "OldBottle" in farm and farm["OldBottle"] != ""
                    else 0
                    for farm in data1["farms"]
                ],
                "Seaweed": [
                    farm["Seaweed"]
                    if "Seaweed" in farm and farm["Seaweed"] != ""
                    else 0
                    for farm in data1["farms"]
                ],
                "Iron C.": [
                    farm["IronCompass"]
                    if "IronCompass" in farm and farm["IronCompass"] != ""
                    else 0
                    for farm in data1["farms"]
                ]
                # 'Davy Jones': ['YES' if int(farm.get('DavyJones', 0)) >= 1
                # else 'NO' for farm in data1['farms']]
            }
        )

        # Remove rows with missing ticket counts
        df1: DataFrame = df1.dropna(subset=["Tickets"])
        # df3 = df3.dropna(subset=['Wild Mushroom'])

        # # MAKE SURE TOP 10 SHOWS
        # top_ten_ids = fetch_top_ten_ids()
        # lanterns_data = retrieve_lanterns_data(top_ten_ids)
        # #lanterns_data = {}
        # existing_ids = df2['Farm'].tolist()
        # new_ids = []

        # for farm_id in lanterns_data.keys():
        #     if farm_id not in existing_ids:
        #         new_ids.append(farm_id)
        #         lantern_data = lanterns_data[farm_id]
        #         new_row = {
        #             'Farm': farm_id,
        #             'Week 8': lantern_data.get('8', 0),
        #             'Week 7': lantern_data.get('7', 0),
        #             'Week 6': lantern_data.get('6', 0),
        #             'Week 5': lantern_data.get('5', 0),
        #             'Week 4': lantern_data.get('4', 0),
        #             'Week 3': lantern_data.get('3', 0),
        #             'Week 2': lantern_data.get('2', 0),
        #             'Week 1': lantern_data.get('1', 0)
        #         }
        #         df2 = pd.concat([df2, pd.DataFrame(new_row, index=[0])],
        # ignore_index=True)
        # Remove emphy columns
        df2: DataFrame = df2.dropna(axis=1, how="all")

        # Count the number of farms that have crafted at least 5
        # lanterns in all the weeks
        count_farms: int = (
            (
                df2[
                    [
                        "Week 8",
                        "Week 7",
                        "Week 6",
                        "Week 5",
                        "Week 4",
                        "Week 3",
                        "Week 2",
                        "Week 1",
                    ]
                ]
                >= 5
            ).all(axis=1)
        ).sum()

        # Count the number of farms that have crafted at least 5 lanterns
        # in all the weeks
        count_farms2: int = (
            (
                df2[
                    [
                        "Week 8",
                        "Week 7",
                        "Week 6",
                        "Week 5",
                        "Week 4",
                        "Week 3",
                        "Week 2",
                        "Week 1",
                    ]
                ]
                >= 1
            ).all(axis=1)
        ).sum()

        # Convert Total Ticket column to numeric values
        df1["Tickets"] = pd.to_numeric(df1["Tickets"])
        df2["Week 8"] = pd.to_numeric(df2["Week 8"])
        df3["Bottles"] = pd.to_numeric(df3["Bottles"])
        df3["Seaweed"] = pd.to_numeric(df3["Seaweed"])
        df3["Iron C."] = pd.to_numeric(df3["Iron C."])

        df3["Points"] = (
            df3["Bottles"].clip(upper=50) * 1.2
            + df3["Seaweed"].clip(upper=25) * 0.4
            + df3["Iron C."].clip(upper=15) * 2
        )

        # Reorder the columns
        # df3 = df3.reindex(columns=['Farm', 'Points', 'Old Bottle',
        # 'Seaweed', 'Iron Compass'])
        # Format the Points column
        df3["Points"] = df3["Points"].round(2)
        # df3['Points'] = df3['Points'].apply(lambda x: f'{x:.2f}')

        # Sort by Total Ticket in descending order
        df1 = df1.sort_values(by="Tickets", ascending=False)
        df2 = df2.sort_values(by="Week 8", ascending=False)
        df3: DataFrame = df3.sort_values(by="Points", ascending=False)
        # ['Bottles', 'Iron C.', 'Seaweed'],
        # ascending=[False, False, False], kind='mergesort')

        df2 = df2.rename(columns={"Week 8": "Week 8 🔻"})
        # df3= df3.rename(columns={"Points": "Points 🔻"})

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
            main_app.rank_tab_cons["live_update"].error(
                "The ranking is currently not working, it will be fixed soon™ "
            )
        else:
            in_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
            out_fmt = "%Y-%m-%d %H:%M"
            update: str = datetime.strptime(
                data1["updatedAt"], in_fmt
            ).strftime(out_fmt)
            main_app.rank_tab_cons["live_update"].success(
                f"🕘Updated at: **{update} UTC**"
            )

            # if buttonok2:
            #     df1 = df1.loc[df1["Farm"].str.contains(text_search)]
            #     main_app.rank_tab_cons["live_ranking"].write(df1)
            #     df2 = df2.loc[df2["Farm"].str.contains(text_search)]
            #     main_app.rank_tab_cons["live_lantern"].write(df2)
            #     main_app.rank_tab_cons["live_minted"].info(
            #         f"🕯️ **Farms with 1 Lantern each week: {count_farms2}**"
            #     )
            #     main_app.rank_tab_cons["live_minted"].success(
            #         f"🏮 **Farms with 5 Lanterns each week: {count_farms}**"
            #     )
            #     df3 = df3.loc[df3["Farm"].str.contains(text_search)]
            #     main_app.rank_tab_cons["live_treasure"].write(df3)
            # else:
            main_app.rank_tab_cons["live_ranking"].write(df1)
            main_app.rank_tab_cons["live_lantern"].write(df2)
            main_app.rank_tab_cons["live_minted"].info(
                f"🕯️ **Farms with 1 Lantern each week: {count_farms2}**"
            )
            main_app.rank_tab_cons["live_minted"].success(
                f"🏮 **Farms with 5 Lanterns each week: {count_farms}**"
            )
            main_app.rank_tab_cons["live_treasure"].data_editor(
                df3,
                column_config={
                    "Points": st.column_config.ProgressColumn(
                        "Points 🔻",
                        help="Click here to change the ranking based in "
                        + "Points",
                        # width="medium",
                        format="%.2f",
                        min_value=0,
                        max_value=100,
                    ),
                },
                hide_index=False,
                disabled=True,
            )
        pass
    except Exception as e:
        main_app.rank_tab_cons["live_update"].error(
            f"The ranking is currently not working, it will be fixed soon™, "
            + f"Error: {str(e)}"
        )


if __name__ == "__main__":
    asyncio.run(main())

# with tab8:
#     col_nft, buff11 = st.columns([2,2])
#     with col_nft:
#         st.error(f"The NFT List is momentarely disable,
# it will be enable back soon™")
