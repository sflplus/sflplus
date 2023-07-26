import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from typing import TYPE_CHECKING
import json
import sys
import requests
import pandas as pd

from functions import wearable_list

if TYPE_CHECKING:
    from main import Main


class BumpkinTab:
    def __init__(self, main, tab: DeltaGenerator) -> None:
        self.main: Main = main
        self.tab: DeltaGenerator = tab

        status_ok2: DeltaGenerator = tab.container()

        col18: DeltaGenerator
        col19: DeltaGenerator
        col20: DeltaGenerator
        col21: DeltaGenerator
        col18, col19, col20, col21 = tab.columns([2, 2, 2, 2], gap="medium")
        col18.markdown("##### 🔻 SEARCH BUMPKIN ID 🔻")

        col_search2: DeltaGenerator
        col_ok2: DeltaGenerator
        col_search2, col_ok2 = col18.columns([2, 2])

        text_search: str = col_search2.text_input(
            "🔻 SEARCH BUMPKIN ID 🔻",
            label_visibility="collapsed",
            max_chars=5,
        )
        buttonok3: bool = col_ok2.button("OK", key="OK3")
        bump_worth_how2: DeltaGenerator = col18.expander(
            "📝 **HOW IT WORKS?**", expanded=False
        )
        bump_general2: DeltaGenerator = col18.expander(
            "📖 **GENERAL**", expanded=True
        )
        bump_info2: DeltaGenerator = col19.expander("🖼️ PICTURE", expanded=True)
        bump_wearables2: DeltaGenerator = col20.expander(
            "👖 **WEARABLES**", expanded=True
        )
        bump_skill2: DeltaGenerator = col21.expander(
            "🏹 **SKILLS & ACHIEVEMENTS**", expanded=True
        )

        if buttonok3:
            text_search_strip: str = (
                text_search.strip()
            )  # Get the value of text_search2 and remove spaces
            if not text_search_strip:
                return
            try:
                text_search_value = int(text_search_strip)  # Convert to integer
            except ValueError:
                status_ok2.error(
                    "Invalid Bumpkin ID. Please enter a valid numeric ID."
                )
                sys.exit()  # Stop execution if the ID is invalid

            url = "https://api.sunflower-land.com/community/getBumpkins"
            payload: str = json.dumps({"ids": [text_search_value]})
            headers: dict[str, str] = {"Content-Type": "application/json"}
            try:
                response2: dict = requests.request(
                    "POST", url, headers=headers, data=payload
                ).json()
            except requests.exceptions.RequestException as e:
                status_ok2.error(
                    "Error: Too many requests, please try again "
                    + "in a few seconds"
                )
                # Stop execution if there is an API connection error
                sys.exit()
            if "bumpkins" not in response2:
                status_ok2.error("Invalid response or error occurred.")
                return
            bumpkins = response2["bumpkins"]
            if str(text_search_value) not in bumpkins:
                status_ok2.error(f"Bumpkin {text_search} not found.")
                return
            bumpkin2 = bumpkins[str(text_search_value)]
            if bumpkin2 is None:
                status_ok2.error(
                    f"The Bumpkin **{text_search}** it isn't in the "
                    + "Bumpkins API, you can try to search it on "
                    + "this site instead:"
                )
                status_ok2.markdown(
                    '🔗 <a href="https://sfl.shen.cyou/bumpkins" '
                    + 'target="_blank">https://sfl.shen.cyou/bumpkins</a>',
                    unsafe_allow_html=True,
                )
                return
            status_ok2.success(
                f" ✅ Done! Bumpkin **{text_search_value}** loaded."
            )
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
                # fmt: off
                bump_url_last2 = bump_url2[
                    image_url2 + len("v1_"):
                ]
                # fmt: on
                bump_img_url2: str = (
                    f'<img src="https://images.bumpkins.io/'
                    + f'nfts/{bump_url_last2}.png" width = 100%>'
                )
            else:
                bump_img_url2: str = ""

            bump_general2.info(f" #️⃣ **Bumpkin ID: #{text_search}**")

            current_lvl2 = None
            for level, info in self.main.xp_dict.items():
                if bump_xp2 >= info["Total XP"]:
                    current_lvl2 = level

            if current_lvl2 is None:
                current_lvl2: int | None = max(self.main.xp_dict.keys())

            if current_lvl2 == max(self.main.xp_dict.keys()):
                xp_needed2 = "N/A"
                nextlvl_xp2 = "N/A"
                extra_xp2 = "N/A"
            else:
                if current_lvl2 in self.main.xp_dict:
                    level_info2 = self.main.xp_dict[current_lvl2]
                    xp_needed2 = level_info2["XP_next"] - (
                        bump_xp2 - level_info2["Total XP"]
                    )
                    nextlvl_xp2 = level_info2["XP_next"]
                    extra_xp2 = nextlvl_xp2 - xp_needed2
                else:
                    xp_needed2 = "N/A"
                    nextlvl_xp2 = "N/A"
                    extra_xp2 = "N/A"

            level_price2 = (bump_xp2 / 500) * self.main.sfl_price
            # Check if the values are floats before rounding

            filtered_df2 = wearable_list(
                self.main,
                equipped_dict,
                return_type="filtered_df",
            )
            total_value_wearable2 = wearable_list(
                self.main, equipped_dict, return_type="total"
            )
            bump_price_usd2 = total_value_wearable2 + level_price2

            bump_info2.markdown(bump_img_url2, unsafe_allow_html=True)
            bump_info2.write("\n")
            bump_info2.success(
                f"\n📊 Total Worth Estimate: **${bump_price_usd2:.2f}**"
            )

            bump_worth_how2.info(
                "The value of **Levels Price** are calculated "
                + "using **500 XP = 1 SFL**, considering "
                + "this kinda as average value cost of the "
                + "most used meals XP and lowered a little "
                + 'bit to also **"value the time"**.'
            )
            bump_worth_how2.success(
                "For **Bumpkin Wearables**, it uses the "
                + "**average between the last sold price "
                + "and the current lowest listing price on "
                + "OpenSea**, which is updated 1-2 times per "
                + "day (semi-manually)."
            )

            bump_general2.write(f" - 📗 Current Level: **{current_lvl2}**")
            bump_general2.write(
                f" - 📘 Current Total XP: **{round(bump_xp2, 1)}**"
            )
            if current_lvl2 == max(self.main.xp_dict.keys()):
                bump_general2.write(f" - 📙 Current Progress: **(MAX)**")
                bump_general2.write(f" - ⏭️ XP for Next LVL: **(MAX)**")
            else:
                bump_general2.write(
                    f" - 📙 Current Progress: "
                    + f"**[{round(extra_xp2, 1)} / {nextlvl_xp2}]**"
                )
                bump_general2.write(
                    f" - ⏭️ XP for Next LVL: " + f"**{round(xp_needed2, 1)}**"
                )
            bump_general2.write("\n")
            bump_general2.success(
                f"\n📊 Levels Price Estimate: " + f"**${level_price2:.2f}**"
            )

            bump_wearables2.write(filtered_df2)
            bump_wearables2.success(
                f"\n📊 Wearables Total Price: "
                + f"**${total_value_wearable2:.2f}**"
            )

            # Create lists to store the keys and descriptions
            skill_names2: list = []
            skill_descriptions2: list = []

            # Iterate over the dictionary and extract the keys and descriptions
            for key in skills_dict:
                skill_names2.append(key)
                skill_descriptions2.append(
                    self.main.skills_description.get(
                        key, "Description not available"
                    )
                )
            # Create a DataFrame
            df_skills2 = pd.DataFrame(
                {
                    "Skill": skill_names2,
                    "Description": skill_descriptions2,
                }
            )
            df_skills2.set_index("Skill", inplace=True)

            # Write the DataFrame
            bump_skill2.write(df_skills2)
            bump_achi_total2: int = len(bump_achi2)
            bump_skill2.success(
                f"\n🏅 Total Achievements: **{bump_achi_total2}**"
            )
