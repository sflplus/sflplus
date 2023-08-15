from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import pandas as pd
import requests
from pandas import DataFrame, Series
from streamlit.delta_generator import DeltaGenerator

# from functions import fetch_owner_count

if TYPE_CHECKING:
    from main import Main

RANKING_URL = "http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking"


# buttonok2: bool = col_ok.button(
#     "OK", key="rank_ok_btn", on_click=self.load_tab
# )
# self.load_tab()
class RankingTab:
    def __init__(self, main, tab: DeltaGenerator) -> None:
        self.main: Main = main
        self.rt_cons: dict[str, DeltaGenerator] = {}
        self.create_tab(tab)
        # self.load_tab()

    def create_tab(self, tab: DeltaGenerator) -> None:
        tab.markdown("##### 🔻 LOAD RANKINGS 🔻")
        col_ok: DeltaGenerator
        # pylint: disable-next=unused-variable
        col_ok, buff = tab.columns([2.5, 6])
        self.buttonload: bool = col_ok.button("OK", key="rank_load_btn")

        col_rank: DeltaGenerator
        col_rank2: DeltaGenerator
        col_rank3: DeltaGenerator
        col_rank, col_rank2, col_rank3 = tab.columns([2, 2, 1.5])

        self.rt_cons["live_update"] = col_rank.container()
        self.rt_cons["live_xp"] = col_rank.expander(
            "🥇 **BUMPKINS LEADERBOARD**", expanded=True
        )

        col_rank2.info(
            "❤️ **Shoutout to Victor Gianvechio for providing the data.** "
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
        if self.buttonload:
            # self.create_tab(tab)
            self.load_tab()
        else:
            self.rt_cons["live_update"] = col_ok.container()

    def load_tab(self) -> None:
        self.rt_cons["live_how"].info(
            "📌 This is using a **fixed list of 10K of farms**, originally "
            + "used from the Dawn Breaker ranking, and then using the SFL API "
            + "**every 6 hours** to refresh the info of the farms."
        )
        self.rt_cons["live_how"].success(
            "⚠️ **Note that if your farm isn't here you can ask in Discord "
            + "to be manually added, but is only going to be update every "
            + "couple of days.**"
        )
        # self.rt_cons["live_point"].info(
        #     f"**The Point system is using Old Bottles as 1.2 , Seaweed as 0.4"
        #     + " and Iron Compass as 2, all of them are capped to only count "
        #     + "until the quantity needed (50, 25 and 15) giving a score of "
        #     + "100 points if you have enough to mint the Tin Turtle.**"
        # )

        try:
            try:
                # data1: dict[str, Any] = await fetch(url_rank1, session)
                data1: dict[str, Any] = requests.get(
                    RANKING_URL, timeout=5
                ).json()
            except (
                requests.exceptions.JSONDecodeError,
                requests.exceptions.Timeout,
            ):
                self.rt_cons["live_update"].error(
                    "The ranking is currently not working, will be fixed soon™"
                )
                return
            # data2 = await fetch(url_rank2, session)

            df1 = pd.DataFrame(
                {
                    "Farm": [farm["FarmID"] for farm in data1["farms"]],
                    "Bumpkin XP": [
                        farm["B_XP"]
                        if "B_XP" in farm and farm["B_XP"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "Expansion": [
                        farm["Land"]
                        if "Land" in farm and farm["Land"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "SFL Earn": [
                        farm["B_EA"]
                        if "B_EA" in farm and farm["B_EA"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "SFL Spent": [
                        farm["B_SP"]
                        if "B_SP" in farm and farm["B_SP"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                }
            )

            df2 = pd.DataFrame(
                {
                    "Farm": [farm["FarmID"] for farm in data1["farms"]],
                    "Sunflowers": [
                        farm["B_SU"]
                        if "B_SU" in farm and farm["B_SU"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "Trees": [
                        farm["B_WO"]
                        if "B_WO" in farm and farm["B_WO"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "Stone": [
                        farm["B_ST"]
                        if "B_ST" in farm and farm["B_ST"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "Iron": [
                        farm["B_IR"]
                        if "B_IR" in farm and farm["B_IR"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "Gold": [
                        farm["B_GO"]
                        if "B_GO" in farm and farm["B_GO"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "Shovels": [
                        farm["B_SH"]
                        if "B_SH" in farm and farm["B_SH"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                    "Drills": [
                        farm["B_DR"]
                        if "B_DR" in farm and farm["B_DR"] != ""
                        else None
                        for farm in data1["farms"]
                    ],
                }
            )

            # df3 = pd.DataFrame(
            #     {
            #         "Farm": [farm["FarmID"] for farm in data1["farms"]],
            #         "Bottles": [
            #             farm["OldBottle"]
            #             if "OldBottle" in farm and farm["OldBottle"] != ""
            #             else 0
            #             for farm in data1["farms"]
            #         ],
            #         "Seaweed": [
            #             farm["Seaweed"]
            #             if "Seaweed" in farm and farm["Seaweed"] != ""
            #             else 0
            #             for farm in data1["farms"]
            #         ],
            #         "Iron C.": [
            #             farm["IronCompass"]
            #             if "IronCompass" in farm and farm["IronCompass"] != ""
            #             else 0
            #             for farm in data1["farms"]
            #         ]
            # 'Davy Jones': ['YES' if int(farm.get('DavyJones', 0)) >= 1
            # else 'NO' for farm in data1['farms']]
            #     }
            # )

            # Remove rows with missing ticket counts
            df1: DataFrame = df1.dropna(subset=["Bumpkin XP"])
            # df3 = df3.dropna(subset=['Wild Mushroom'])

            # Convert Total Ticket column to numeric values
            df_bump_xp: Any = df1.get("Bumpkin XP")
            df_exp: Any = df1.get("Expansion")
            df_sfl_earned: Any = df1.get("SFL Earn")
            df_sfl_spent: Any = df1.get("SFL Spent")
            assert isinstance(df_bump_xp, Series)
            assert isinstance(df_exp, Series)
            assert isinstance(df_sfl_earned, Series)
            assert isinstance(df_sfl_spent, Series)
            kwargs: dict = {
                "Bumpkin XP": pd.to_numeric(arg=df_bump_xp).round(2)
            }
            kwargs.update({"Expansion": pd.to_numeric(df_exp)})
            kwargs.update({"SFL Earn": pd.to_numeric(df_sfl_earned).round(2)})
            kwargs.update({"SFL Spent": pd.to_numeric(df_sfl_spent).round(2)})
            df1.assign(**kwargs)

            # Create a new column "Level" in the DataFrame
            df1.assign(Level=None)  # Initialize the "Level" column with None

            # Iterate through the DataFrame rows and determine the level based
            # on "Bumpkin XP"
            for index, row in df1.iterrows():
                bump_xp = row["Bumpkin XP"]
                current_lvl: int | None = None

                for level, info in self.main.xp_dict.items():
                    if bump_xp >= info["Total XP"]:
                        current_lvl = level

                if current_lvl is None:
                    current_lvl = max(self.main.xp_dict.keys())

                df1.at[index, "Level"] = current_lvl

            # reorder columns
            df1.reindex(
                [
                    "Farm",
                    "Level",
                    "Bumpkin XP",
                    "Expansion",
                    "SFL Earn",
                    "SFL Spent",
                ],
                axis=1,
            )

            # df2["Week 8"] = pd.to_numeric(df2["Week 8"])
            # df3["Bottles"] = pd.to_numeric(df3["Bottles"])
            # df3["Seaweed"] = pd.to_numeric(df3["Seaweed"])
            # df3["Iron C."] = pd.to_numeric(df3["Iron C."])

            # df3["Points"] = (
            #     df3["Bottles"].clip(upper=50) * 1.2
            #     + df3["Seaweed"].clip(upper=25) * 0.4
            #     + df3["Iron C."].clip(upper=15) * 2
            # )

            # Reorder the columns
            # df3 = df3.reindex(columns=['Farm', 'Points', 'Old Bottle',
            # 'Seaweed', 'Iron Compass'])
            # Format the Points column
            # df3["Points"] = df3["Points"].round(2)
            # df3['Points'] = df3['Points'].apply(lambda x: f'{x:.2f}')

            # Sort by Total Ticket in descending order
            df1 = df1.sort_values(by="Bumpkin XP", ascending=False)
            df2: DataFrame = df2.sort_values(by="Sunflowers", ascending=False)
            # df3: DataFrame = df3.sort_values(by="Points", ascending=False)
            # ['Bottles', 'Iron C.', 'Seaweed'],
            # ascending=[False, False, False], kind='mergesort')

            df1 = df1.rename(columns={"Bumpkin XP": "Bumpkin XP 🔻"})
            df2 = df2.rename(columns={"Sunflowers": "Sunflowers 🔻"})

            # Reset index and set the "Ranking" column as the new index
            df1 = df1.reset_index(drop=True)
            df2 = df2.reset_index(drop=True)
            # df3 = df3.reset_index(drop=True)

            df1.index = df1.index + 1
            df2.index = df2.index + 1
            # df3.index = df3.index + 1

            # Rename the index to "Ranking"
            df1.index.name = "Rank"
            df2.index.name = "Rank"
            # df3.index.name = "Rank"

            # Convert index to integer values
            df1.index = df1.index.astype(int)
            df2.index = df2.index.astype(int)
            # df3.index = df3.index.astype(int)

            if df1.empty:
                self.rt_cons["live_update"].error(
                    " The ranking is currently not working, it will "
                    + "be fixed soon™ "
                )
            else:
                in_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
                out_fmt = "%Y-%m-%d %H:%M"
                update: str = datetime.strptime(
                    data1["updatedAt"], in_fmt
                ).strftime(out_fmt)
                self.rt_cons["live_update"].success(
                    f"🕘Updated at: **{update} UTC**"
                )

                self.rt_cons["live_xp"].write(df1)
                self.rt_cons["live_resources"].write(df2)
        # pylint: disable-next=broad-exception-caught
        except Exception as exception:
            self.rt_cons["live_update"].error(
                " 3 The ranking is currently not working, it will "
                + f"be fixed soon™, Error: {str(exception)}"
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
            minutes_remaining = int(
                (time_remaining.total_seconds() % 3600) // 60
            )
            # Calculate the time and date of the next 50th respawn
            # timestamp2 = 1685779200
            # dt2: datetime = datetime.fromtimestamp(timestamp2)
            # time_remaining2: timedelta = dt2 - datetime.fromtimestamp(
            #     current_time
            # )
            # days_remaining2: int = time_remaining2.days
            # hours_remaining2: int = time_remaining2.seconds // 3600
            # minutes_remaining2: int = (time_remaining2.seconds % 3600) // 60
            # formatted_time_remaining: str = (
            #     "{} Days {:02d}:{:02d} hours".format(
            #         days_remaining2, hours_remaining2, minutes_remaining2
            #     )
            # )
            self.rt_cons["live_mush"].info(
                "📊 **Total Respawns: {}**".format(int(respawns))
            )
            self.rt_cons["live_mush"].success(
                "⏭️ **Next Respawn in: {:02d}:{:02d} hours**".format(
                    hours_remaining, minutes_remaining
                )
            )

    def get_containers(self) -> dict[str, DeltaGenerator]:
        return self.rt_cons
