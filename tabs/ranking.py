import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from typing import Any, TYPE_CHECKING
from datetime import timedelta, datetime
import pandas as pd
from pandas import DataFrame
from functions import fetch_owner_count
if TYPE_CHECKING:
    from main import Main
        # tab.markdown("##### 🔻 SEARCH FARM ID 🔻")
        # col_search: DeltaGenerator
        # col_ok: DeltaGenerator
        # buff: DeltaGenerator
        # col_search, col_ok, buff = tab.columns([2.5, 2, 6])
        # text_search: str = col_search.text_input(
        #     "🔻 SEARCH FARM ID  🔻",
        #     label_visibility="collapsed",
        #     max_chars=6,
        #     value=self.main.farm_id,
        # )
        # self.create_tab(tab)
        # buttonok2: bool = col_ok.button(
        #     "OK", key="rank_ok_btn", on_click=self.load_tab
        # )
        # self.load_tab()
class RankingTab:
    def __init__(self, main, tab: DeltaGenerator) -> None:
        self.main: Main = main
        self.rt_cons: dict[str, DeltaGenerator] = {}
        self.create_tab(tab)       
        self.load_tab()
        
        # tab.markdown("##### 🔻 LOAD RANKINGS 🔻")
        # self.buttonload: bool = tab.button(
        #     "OK", key="rank_load_btn"
        # )
        # col_ok: DeltaGenerator
        # col_ok, buff = tab.columns([2.5, 6])

        # if self.buttonload:
        #     self.create_tab(tab)
        #     self.load_tab()
        # else:
        #     self.rt_cons["live_update"] = col_ok.container()




    def create_tab(self, tab: DeltaGenerator) -> None:
        col_rank: DeltaGenerator
        col_rank2: DeltaGenerator
        col_rank3: DeltaGenerator
        col_rank, col_rank2, col_rank3 = tab.columns([2, 2, 1.5])
    
        self.rt_cons["live_update"] = col_rank.container()
        self.rt_cons["live_xp"] = col_rank.expander(
            "🥇 **BUMPKINS LEADERBOARD**", expanded=True
        )
    
        col_rank2.info(
            f"❤️ **Shoutout to Victor Gianvechio for providing the data.** "
        )
        self.rt_cons["live_resources"] = col_rank2.expander(
            "🏅 **ACTIVITIES LEADERBOARD**", expanded=True
        )
    
        self.rt_cons["live_how"] = col_rank3.expander(
            "📝 **HOW IT WORKS?**", expanded=True
        )
        self.rt_cons["live_mush"] = col_rank3.expander(
            "🍄 **WILD MUSHROOM**", expanded=True
            )    
        
        # self.rt_cons["live_point"] = col_rank.expander(
        #     "🥇 **POINTS SYSTEM**", expanded=False
        # )
        # self.rt_cons["live_minted"] = col_rank.expander(
        #     "⚡ **CURRENT MINTS**", expanded=True
        # )        
        # self.rt_cons["live_ranking"] = col_rank3.expander(
        #     "🎟️ **DAWN BREAKER TICKETS**", expanded=True
        # )
        # self.rt_cons["live_minted_error"] = col_rank3.container()   
    def load_tab(self) -> None:
        self.rt_cons["live_how"].info(
            f"📌 This is using a **fixed list of 10K of farms**, originally used "
            + "from the Dawn Breaker ranking, and then using the SFL API **every 6 hours** to "
            + "refresh the info of the farms."
        )
        self.rt_cons["live_how"].success(
            f"⚠️ **Note that if your farm isn't here you can ask in Discord "
            + "to be manually added, but is only going to be update every couple "
            + "of days.**"
        )
        # self.rt_cons["live_point"].info(
        #     f"**The Point system is using Old Bottles as 1.2 , Seaweed as 0.4 "
        #     + "and Iron Compass as 2, all of them are capped to only count "
        #     + "until the quantity needed (50, 25 and 15) giving a score of "
        #     + "100 points if you have enough to mint the Tin Turtle.**"
        # )
        first_respawn = 1682899200
        respawn_interval = timedelta(hours=16)
        current_time: float = datetime.now().timestamp()
        respawns: float = (
            current_time - first_respawn
        ) // respawn_interval.total_seconds()
        next_respawn: datetime = (
            datetime.fromtimestamp(first_respawn)
            + (respawns + 1) * respawn_interval
        )
        time_remaining: timedelta = next_respawn - datetime.fromtimestamp(
            current_time
        )
        hours_remaining = int(time_remaining.total_seconds() // 3600)
        minutes_remaining = int((time_remaining.total_seconds() % 3600) // 60)
        # Calculate the time and date of the next 50th respawn
        timestamp2 = 1685779200
        dt2: datetime = datetime.fromtimestamp(timestamp2)
        time_remaining2: timedelta = dt2 - datetime.fromtimestamp(current_time)
        days_remaining2: int = time_remaining2.days
        hours_remaining2: int = time_remaining2.seconds // 3600
        minutes_remaining2: int = (time_remaining2.seconds % 3600) // 60
        formatted_time_remaining: str = "{} Days {:02d}:{:02d} hours".format(
            days_remaining2, hours_remaining2, minutes_remaining2
        )
        self.rt_cons["live_mush"].info(
            "📊 **Total Respawns: {}**".format(int(respawns))
        )
        self.rt_cons["live_mush"].success(
            "⏭️ **Next Respawn in: {:02d}:{:02d} hours**".format(
                hours_remaining, minutes_remaining
            )
        )
        # Iterate over the list of queries and retrieve the owner counts
        def create_dataframe() -> DataFrame:
            data: list = []
            for i, query_id in enumerate(self.main.queries):
                if self.main.queries_owners[i] is not None:
                    owner_count = int(
                        self.main.queries_owners[i]
                    )  # Convert owner count to integer
                else:
                    owner_count: int | None = fetch_owner_count(
                        query_id, self.main.API_KEY_DUNE
                    )
                query_name: str = self.main.queries_name[i]
                query_emoji: str = self.main.queries_emoji[i]
                query_quantity: str = self.main.queries_quantity[i]
                # query_ticket = queries_ticket[i]
                nft: str = f"{query_emoji} {query_name}"
                data.append([nft, owner_count, query_quantity])  # query_ticket
            # Create a dataframe from the data list
            df_dune = pd.DataFrame(
                data, columns=["NFT", "Owners", "Supply"]
            )  # "Tickets"
            return df_dune
        # Create or fetch the cached dataframe
        # @st.cache_data(ttl=30)
        def get_cached_dataframe() -> DataFrame:
            try:
                return create_dataframe()
            except Exception as e:
                st.error(f"Failed to fetch NFT mints. Error: {e}")
                return pd.DataFrame()
        # df_dune: DataFrame = get_cached_dataframe()
        # live_minted.info(f"👨‍🔬 **This info is from Dune**")
        # Display the dataframe
        # self.rt_cons["live_minted"].dataframe(df_dune, hide_index=True)    
    def get_containers(self) -> dict[str, DeltaGenerator]:
        return self.rt_cons
