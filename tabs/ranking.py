import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from typing import Any, TYPE_CHECKING
from datetime import timedelta, datetime
import pandas as pd
from pandas import DataFrame

from functions import fetch_owner_count

if TYPE_CHECKING:
    from main import Main


class RankingTab:
    def __init__(self, main, tab: DeltaGenerator) -> None:
        self.main: Main = main
        tab.markdown("##### 🔻 SEARCH FARM ID 🔻")

        col_search: DeltaGenerator
        col_ok: DeltaGenerator
        buff: DeltaGenerator
        col_search, col_ok, buff = tab.columns([2.5, 2, 6])
        text_search: str = col_search.text_input(
            "🔻 SEARCH FARM ID  🔻",
            label_visibility="collapsed",
            max_chars=6,
            value=self.main.farm_id,
        )
        self.create_tab(tab)

        buttonok2: bool = col_ok.button(
            "OK", key="rank_ok_btn", on_click=self.load_tab
        )
        self.load_tab()

    def create_tab(self, tab: DeltaGenerator) -> None:
        self.rt_cons: dict[str, DeltaGenerator] = {}
        col_rank: DeltaGenerator
        col_rank2: DeltaGenerator
        col_rank3: DeltaGenerator
        col_rank, col_rank2, col_rank3 = tab.columns([3, 3, 3])
        self.rt_cons["live_how"] = col_rank.expander(
            "📝 **HOW IT WORKS?**", expanded=False
        )
        self.rt_cons["live_treasure"] = col_rank.expander(
            "🐢 **TURTLES RACE**", expanded=True
        )
        self.rt_cons["live_point"] = col_rank.expander(
            "🥇 **POINTS SYSTEM**", expanded=False
        )
        self.rt_cons["live_minted"] = col_rank.expander(
            "⚡ **CURRENT MINTS**", expanded=True
        )

        self.rt_cons["live_update"] = col_rank2.container()
        self.rt_cons["live_lantern"] = col_rank2.expander(
            "🏮 **LANTERNS RANKING**", expanded=True
        )
        self.rt_cons["live_odds"] = col_rank2.expander(
            "🎲 **ODDS OF DIGGING**", expanded=True
        )
        self.rt_cons["live_mush"] = col_rank2.expander(
            "🍄 **WILD MUSHROOM**", expanded=True
        )

        col_rank3.info(
            f"❤️ **Shoutout to Victor Gianvechio for providing the data.** "
        )
        self.rt_cons["live_ranking"] = col_rank3.expander(
            "🎟️ **DAWN BREAKER TICKETS**", expanded=True
        )
        self.rt_cons["live_minted2"] = col_rank3.expander(
            "🐢 **TURTLES REQUIREMENTS**", expanded=True
        )
        self.rt_cons["live_minted_error"] = col_rank3.container()

        # live_calculator = st.expander("🤖 **LANTERNS CALCULATOR**",
        # expanded=True)

        # from_lanterns = live_calculator.number_input("🔺 From How Many
        # Lanters?", min_value=0, max_value=999, step=1)
        # to_lanterns = live_calculator.number_input("🔻To How Many?",
        # min_value=0, max_value=999, step=1, value=5)
        # check_banner = live_calculator.checkbox("You have the Dawn Breaker
        # Banner?", value=True, on_change=None,label_visibility="visible")
        # buttonok4 = live_calculator.button('OK', key="OK4")
        # emojis_resources = emojis
        # if buttonok4:
        #     try:
        #         lanterns_ing, lanterns_sfl = retrieve_lantern_ingredients()

        #         accumulated_lanterns_ing = {}
        #         accumulated_lanterns_sfl = 0.0

        #         if lanterns_sfl is not None:
        #             accumulated_lanterns_sfl = lanterns_sfl *
        # (to_lanterns * (to_lanterns + 1) / 2)

        #         if from_lanterns > 0:
        #             from_lanterns_ing = {}
        #             from_lanterns_sfl = 0.0

        #             if lanterns_sfl is not None:
        #                 from_lanterns_sfl = lanterns_sfl *
        # (from_lanterns * (from_lanterns + 1) / 2)

        #             for lantern_count in range(from_lanterns + 1):
        #                 for ingredient, quantity in lanterns_ing.items():
        #                     if ingredient not in from_lanterns_ing:
        #                         from_lanterns_ing[ingredient] = 0
        #                     from_lanterns_ing[ingredient] += int(quantity)
        # * lantern_count

        #             accumulated_lanterns_ing = from_lanterns_ing
        #             extra_lanterns_sfl = accumulated_lanterns_sfl -
        # from_lanterns_sfl
        #         else:
        #             extra_lanterns_sfl = accumulated_lanterns_sfl

        #         extra_lanterns_sfl_banner = extra_lanterns_sfl * 0.75
        #         extra_lanterns_ing = {}

        #         for ingredient, quantity in lanterns_ing.items():
        #             if ingredient == "Block Buck":
        #                 extra_quantity = to_lanterns - from_lanterns
        # # Fixed 1 per lantern
        #             else:
        #                 extra_quantity = int(quantity) * (to_lanterns
        # * (to_lanterns + 1) / 2) - accumulated_lanterns_ing.get(ingredient, 0)
        #             extra_lanterns_ing[ingredient] = extra_quantity

        #         live_calculator.info(f"\n👨‍🏫 **Resources From
        # {from_lanterns} to {to_lanterns} Lanterns:**")
        #         #live_calculator.write(f"- 💰 SFL: **{lanterns_ing}**")
        #         for ingredient, quantity in extra_lanterns_ing.items():
        #             live_calculator.write(f" - {emojis.get(ingredient)}
        # {ingredient}: **{quantity:.0f}**")
        #         if lanterns_sfl is not None:
        #             if check_banner:
        #                 live_calculator.write(f"- 💰 SFL:
        # **{extra_lanterns_sfl_banner:.2f}**")
        #             else:
        #                 live_calculator.write(f"- 💰 SFL:
        # **{extra_lanterns_sfl:.2f}**")
        #     except Exception as e:
        #         live_calculator.error(f"Error: {str(e)}")

    def load_tab(self) -> None:
        self.rt_cons["live_how"].info(
            f"📌 **This is using Dawn Breaker Tickets Dune query to get the "
            + "TOP 10000 farms and then using the SFL API every 30~ min to "
            + "refresh the info of the farms.**"
        )
        self.rt_cons["live_how"].info(
            f"⚠️ **Note that if your farm isn't in the TOP 10000 of the Dawn "
            + "Breaker Tickets Dune query, is not going to show up in this "
            + "Live Rankings.**"
        )

        self.rt_cons["live_point"].info(
            f"**The Point system is using Old Bottles as 1.2 , Seaweed as 0.4 "
            + "and Iron Compass as 2, all of them are capped to only count "
            + "until the quantity needed (50, 25 and 15) giving a score of "
            + "100 points if you have enough to mint the Tin Turtle.**"
        )

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

        # live_mush.warning("🚨 **50th Respawn in: {}**".
        # format(formatted_time_remaining))
        # live_mush.markdown("##### 🍄 **WILD MUSHROOM RANKING**")

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

        df_dune: DataFrame = get_cached_dataframe()

        # live_minted.info(f"👨‍🔬 **This info is from Dune**")
        # Display the dataframe
        self.rt_cons["live_minted"].dataframe(df_dune, hide_index=True)

        self.rt_cons["live_odds"].info(
            f"📝 *Note: This data was calculated using the weight numbers in "
            + f"the Treasure Island Docs 06/06/2023 and the 1 in X are "
            + f"approximations.*"
        )
        self.rt_cons["live_odds"].write(
            f"- 🍾 Old Bottle: **5.19%** (1 in 19 with Shovels)"
        )
        self.rt_cons["live_odds"].write(
            f"- 🌿 Seaweed: **2.60%** (1 in 38 with Shovels)"
        )
        self.rt_cons["live_odds"].write(
            f"- 🧭 Iron Compasss: **0.52%** (1 in 192 with Shovels)"
        )
        self.rt_cons["live_odds"].write(
            f"- 🍾🌿 You **CAN'T** dig a Old Bottle/Seaweed with Drills"
        )
        self.rt_cons["live_odds"].write(
            f"- 🧭 Iron Compasss: **9.50%** (1 in 10 with Drills)"
        )

        self.rt_cons["live_minted2"].info(f" 🐢 **Emerald Turtle: Supply 100**")
        self.rt_cons["live_minted2"].write(
            f"- 🍾 **80** Old Bottles - 🌿 **50** Seaweed"
        )
        self.rt_cons["live_minted2"].write(
            f"- 🧭 **30** Iron Compass - 💰 **100** SFL"
        )
        self.rt_cons["live_minted2"].write("\n")
        self.rt_cons["live_minted2"].success(f" 🥫 **Tin Turtle: Supply 3000**")
        self.rt_cons["live_minted2"].write(
            f"- 🍾 **50** Old Bottles - 🌿 **25** Seaweed"
        )
        self.rt_cons["live_minted2"].write(
            f"- 🧭 **15** Iron Compass - 💰 **40** SFL"
        )

    def get_containers(self) -> dict[str, DeltaGenerator]:
        return self.rt_cons
