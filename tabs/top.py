import streamlit as st
from datetime import datetime, timedelta
from streamlit.delta_generator import DeltaGenerator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Main


class TopTab:
    DC_THREAD_URL = (
        "https://discord.com/channels/880987707214544966/"
        + "1087607534967341087/1087607534967341087"
    )
    DC_NANCY_URL = "https://discord.gg/faz4EkJVab"
    DC_GITHUB_URL = "https://github.com/sflplus/sflplus"

    def __init__(self, main) -> None:
        self.main: Main = main
        col00: DeltaGenerator
        col0x: DeltaGenerator
        col00, col0x, buff3 = st.columns([1.85, 4, 3])
        col00.markdown(
            "[![Foo](https://sflplus.info/sflplus.png)](https://sflplus.info)"
            + '<span style="vertical-align:bottom;color:rgb(0, 221, 66);'
            + f'font-weight:bold;">{main.version}</span>',
            unsafe_allow_html=True,
        )
        with col0x:
            general_info2: DeltaGenerator = st.container()

            general_info2.markdown(
                f"🔒 We are sorry to let you know that the developent of "
                + f"[SFL+]({self.DC_GITHUB_URL}) has come to a end and is "
                + f"not longer going to be updated, read more about "
                + f"[here]({self.DC_THREAD_URL}). We recomend you to use "
                + f"[sfl.world](https://sfl.world) instead as web alternative "
                + f"or [Nancy]({self.DC_NANCY_URL}) for automatic "
                + f"notifications on Discord/Telegram."
            )

        st.divider()
