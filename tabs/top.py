import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Main


class TopTab:
    DC_THREAD_URL = (
        "https://discord.com/channels/880987707214544966/"
        + "1087607534967341087/1087607534967341087"
    )

    def __init__(self, main) -> None:
        self.main: Main = main
        col00: DeltaGenerator
        col11x: DeltaGenerator
        col0x: DeltaGenerator
        col10x: DeltaGenerator
        col00, col11x, col0x, col10x = st.columns([1.85, 1.75, 1.75, 3.5])
        col00.markdown(
            "[![Foo](https://sflplus.info/sflplus.png)](https://sflplus.info)"
            + '<span style="vertical-align:bottom;color:rgb(0, 221, 66);'
            + f'font-weight:bold;">{main.version}</span>',
            unsafe_allow_html=True,
        )
        with col11x:
            general_info: DeltaGenerator = st.container()
            if main.sfl_supply is not None:
                format_supply: str = "{:,.0f}".format(main.sfl_supply / 1e18)
                supply_progress: float = 10000000 - (
                    float(format_supply.replace(",", "")) - 30000000
                )
            else:
                general_info.error(
                    "Failed to get SFL Supply. Please try again later."
                )
                format_supply = "N/A"
                supply_progress = 0
        with col0x:
            general_info2: DeltaGenerator = st.container()

        with col10x:
            general_info3: DeltaGenerator = st.container()

            supply_progress_per: float = (supply_progress / 10000000) * 100
            supply_percentage_float = float(supply_progress_per)
            supply_percentage_number: str = "{:.2f}".format(
                supply_percentage_float
            )
            supply_progress_percentage: float = 100 - float(
                supply_percentage_number
            )
            supply_percentage_final: float = (
                float(supply_percentage_number) / 100
            )
            supply_percentage_inv: float = 1 - supply_percentage_final

            # current_time = datetime.now().timestamp()
            # timestamp3 = 1688947200
            # dt3 = datetime.fromtimestamp(timestamp3)

            # time_remaining3 = dt3 - datetime.fromtimestamp(current_time)
            # days_remaining3 = time_remaining3.days
            # hours_remaining3 = time_remaining3.seconds // 3600
            # minutes_remaining3 = (time_remaining3.seconds % 3600) // 60

            # formatted_time_remaining2 = "{} Days and {:02d}:{:02d} hours".
            # format(days_remaining3, hours_remaining3, minutes_remaining3)

            general_info.write(
                f" 🟣 Matic: **{main.matic_price:.2f}** - "
                + f"🌻 SFL: **{main.sfl_price:.4f}**"
            )
            general_info.write(f" 📈 Current Supply: **{format_supply}**")
            general_info2.write(f" ⏳ Next Halvening: **40,000,000**")
            general_info2.write(
                f" 📊 In Percentage: **{supply_progress_percentage:.2f}%**"
            )
            # general_info2.write("⏳ **{}**".format(formatted_time_remaining2))
            # general_info2.write(f" ⏳ {formatted_time_remaining2}")
            # general_info.progress(supply_percentage_inv, text=None)
            # features_info = st.expander("📗 **FEATURES**", expanded=False)

        st.divider()
        general_info3.markdown(
            f"💬 Feedback? Tag me `@Vitt0c` or use this "
            + f"[Discord thread]({self.DC_THREAD_URL})"
        )
        general_info3.markdown(
            "☕ Donations Wallet: `0x24C262a7c49F8BBc889688A0cb0Fea97d04839c5`"
        )
        # features_info.write(f" - 💎 Farm Worth  - 🏝️ Farm Resources \n -
        #  🚜 Hoarder Limit - 🤑 Spent Checker \n - 👜 Basket Checker
        # - 💰 SFL Balance \n - 🍒 Fruits Harvest Left  - 👨‍🌾 Bumpkins Stats \n
        #  - 🐔 Mutant Chickens ")
