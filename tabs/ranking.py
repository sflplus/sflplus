from datetime import datetime
import streamlit as st
from typing import TYPE_CHECKING, Any
import json

import pandas as pd
import requests
from pandas import DataFrame
from streamlit.delta_generator import DeltaGenerator

if TYPE_CHECKING:
    from main import Main

# RANKING_URL = "http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking"


class RankingTab:
    def __init__(self, main, tab: DeltaGenerator) -> None:
        self.main: Main = main
        self.rt_cons: dict[str, DeltaGenerator] = {}
        self.create_tab(tab)

    def create_tab(self, tab: DeltaGenerator) -> None:
        tab.markdown("##### 🔻 LOAD RANKINGS 🔻")
        col_ok: DeltaGenerator
        [col_ok] = tab.columns([2.5])
        self.buttonload: bool = col_ok.button("OK", key="rank_load_btn")

        [live_update, _, _] = tab.columns([2, 2, 1.5])
        self.rt_cons["live_update"] = live_update.container()

        col_rank: DeltaGenerator
        col_rank2: DeltaGenerator
        col_rank3: DeltaGenerator
        col_rank, col_rank2, col_rank3 = tab.columns([2, 2, 1.5])

        self.rt_cons["live_xp"] = col_rank.expander(
            "🥇 **BUMPKINS LEADERBOARD**", expanded=True
        )

        self.rt_cons["live_resources"] = col_rank2.expander(
            "🏅 **ACTIVITIES LEADERBOARD**", expanded=True
        )

        self.rt_cons["live_how"] = col_rank3.expander(
            "📝 **HOW IT WORKS?**", expanded=True
        )

        [col_potion, col_potion_info, _] = tab.columns([2.6, 1.4, 1.5])
        self.rt_cons["potion_house"] = col_potion.expander(
            "🧪 **POTION HOUSE LEADERBOARD**", expanded=True
        )

        self.rt_cons["potion_info"] = col_potion_info.expander(
            "📊 **POTION HOUSE STATS**", expanded=True
        )

        if self.buttonload:
            self.load_tab()
        else:
            self.rt_cons["live_update"] = col_ok.container()

    # cache for 6 hours
    @st.cache_data(ttl=21600, show_spinner=False)
    def retrieve_rank_data(
        _self,
    ) -> dict:
        BASE_URL = "http://192.168.2.151:1112/api/"
        try:
            main_ranking: dict = requests.get(
                BASE_URL + "main_ranking", timeout=5
            ).json()

            for key, value in main_ranking["data"].items():
                if isinstance(value, str):
                    try:
                        main_ranking["data"][key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass

            secondary_ranking: dict = requests.get(
                BASE_URL + "secondary_ranking", timeout=5
            ).json()

            for key, value in secondary_ranking["data"].items():
                if isinstance(value, str):
                    try:
                        secondary_ranking["data"][key] = json.loads(value)
                    except json.JSONDecodeError:
                        pass

            potion_ranking: dict = requests.get(
                BASE_URL + "potion", timeout=5
            ).json()
            potion_ranking["data"]["stats"] = json.loads(
                potion_ranking["data"]["stats"]
            )

            return {
                "updated_at": main_ranking.get("updated_at", 0),
                "main_ranking": main_ranking["data"],
                "secondary_ranking": secondary_ranking["data"],
                "potion_ranking": potion_ranking["data"],
            }
        except (
            requests.exceptions.JSONDecodeError,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            json.JSONDecodeError,
        ) as e:
            _self.rt_cons["live_update"].error(
                "The ranking is currently not working, "
                + f"will be fixed soon™ {str(e)}"
            )
            st.stop()

    @st.cache_data(ttl=21600, show_spinner="Loading ranked data")
    def build_dataframes(_self, data) -> list[DataFrame]:
        df1 = pd.DataFrame(
            {
                "Farm": list(data["main_ranking"]["experience"].keys()),
                "Bumpkin XP": list(data["main_ranking"]["experience"].values()),
                "Expansion": list(data["main_ranking"]["expansion"].values()),
                "SFL Earned": list(data["main_ranking"]["sfl_earned"].values()),
                "SFL Spent": list(data["main_ranking"]["sfl_spent"].values()),
                "Streak": list(data["main_ranking"]["daily_streak"].values()),
            }
        )

        df2 = pd.DataFrame(
            {
                "Farm": list(data["secondary_ranking"]["sunflower"].keys()),
                "Sunflowers": list(
                    data["secondary_ranking"]["sunflower"].values()
                ),
                "Trees": list(data["secondary_ranking"]["tree"].values()),
                "Stone": list(data["secondary_ranking"]["stone"].values()),
                "Iron": list(data["secondary_ranking"]["iron"].values()),
                "Gold": list(data["secondary_ranking"]["gold"].values()),
                "Shovels": list(data["secondary_ranking"]["dug"].values()),
                "Drills": list(data["secondary_ranking"]["drilled"].values()),
            }
        )

        df3: DataFrame = pd.DataFrame.from_dict(
            data["potion_ranking"]["dataframe"]
        )
        df3 = df3.reindex(
            [
                "Farm",
                "Total Games",
                "Avg. Points",
                "Total Points",
                "Avg. Tickets",
                "Total Tickets",
            ],
            axis=1,
        )

        # Remove rows with missing ticket counts
        # and convert farm numbers to int
        df1: DataFrame = df1.dropna(subset=["Bumpkin XP"])
        df2: DataFrame = df2.dropna(subset=["Sunflowers"])

        df1["Expansion"] = pd.to_numeric(df1["Expansion"])

        # Create a new column "Level" in the DataFrame
        df1.assign(Level=None)  # Initialize the "Level" column with None

        # Iterate through the DataFrame rows and determine the level based
        # on "Bumpkin XP"
        for index, row in df1.iterrows():
            bump_xp = row["Bumpkin XP"]
            current_lvl: int | None = None

            for level, info in _self.main.xp_dict.items():
                if bump_xp >= info["Total XP"]:
                    current_lvl = level

            if current_lvl is None:
                current_lvl = max(_self.main.xp_dict.keys())

            df1.at[index, "Level"] = current_lvl

        # reorder columns
        df1 = df1.reindex(
            [
                "Farm",
                "Bumpkin XP",
                "Level",
                "Expansion",
                "SFL Earned",
                "SFL Spent",
                "Streak",
            ],
            axis=1,
        )

        # Sort by Total Ticket in descending order
        df1 = df1.sort_values(by="Bumpkin XP", ascending=False)
        df2 = df2.sort_values(by="Sunflowers", ascending=False)
        df3 = df3.sort_values(by="Avg. Points", ascending=False)

        df1 = df1.rename(columns={"Bumpkin XP": "Bumpkin XP 🔻"})
        df2 = df2.rename(columns={"Sunflowers": "Sunflowers 🔻"})
        df3 = df3.rename(columns={"Avg. Points": "Avg. Points 🔻"})

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
        return [df1, df2, df3]

    def load_tab(self) -> None:
        self.rt_cons["live_how"].info(
            "📌 The ranking uses the most recent list of farms having a "
            + "towncenter in their inventory. The list is retrieved from "
            + "**dune**, filtered, sorted and truncated to **10,000 farms**."
            + "  \n  \nThe bumpkin leaderboard is sorted by **Bumpkin XP**, the"
            + " activities leaderboard is sorted by **Sunflowers harvested**, "
            + "the potion house leaderboard is sorted by **average points**."
        )
        self.rt_cons["live_how"].success(
            "⚠️ The ranking updated every **12 hours**, the most recent "
            + "update time is displayed above the ranking.  \n  \n"
            + "The minimum amount of games played to appear in the potion "
            + "house leaderboard is currently 50."
        )

        df1: DataFrame
        df2: DataFrame
        df3: DataFrame

        data: dict[str, Any] = self.retrieve_rank_data()
        df1, df2, df3 = self.build_dataframes(data)

        try:
            if df1.empty or df2.empty or df3.empty:
                self.rt_cons["live_update"].error(
                    " The ranking is currently not working, it will "
                    + "be fixed soon™ "
                )
                st.stop()
            out_fmt = "%Y-%m-%d %H:%M"
            update: str = datetime.utcfromtimestamp(
                int(data["updated_at"])
            ).strftime(out_fmt)
            self.rt_cons["live_update"].success(
                f"🕘Updated at: **{update} UTC**"
            )

            self.rt_cons["live_xp"].dataframe(df1, use_container_width=True)
            self.rt_cons["live_resources"].dataframe(
                df2, use_container_width=True
            )
            self.rt_cons["potion_house"].dataframe(
                df3, use_container_width=True
            )

            potion_stats: dict[str, int] = {
                "unique": data["potion_ranking"]["stats"]["unique"],
                "total_games": data["potion_ranking"]["stats"]["total_games"],
                "total_tickets": data["potion_ranking"]["stats"][
                    "total_tickets"
                ],
            }
            self.rt_cons["potion_info"].success(
                f"🕹️ Unique players: {potion_stats['unique']}"
            )
            avg_tickets: float = (
                potion_stats["total_tickets"] / potion_stats["total_games"]
            )
            self.rt_cons["potion_info"].info(
                f"🔥 Total SFL burned: {potion_stats['total_games']}  "
                + f"\n🎫 Avg. tickets per game: {round(avg_tickets, 2)}"
            )
        except KeyError as exception:
            self.rt_cons["live_update"].error(
                " The ranking is currently not working, it will "
                + f"be fixed soon™, Error: {str(exception)}"
            )

    def get_containers(self) -> dict[str, DeltaGenerator]:
        return self.rt_cons
