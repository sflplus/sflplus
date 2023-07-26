from typing import TYPE_CHECKING, Hashable
from decimal import Decimal
import streamlit as st
import requests
from streamlit.delta_generator import DeltaGenerator
from typing import Any
import json
import pandas as pd
from datetime import datetime, timedelta

from functions import nft_price, nft_buffs, wearable_list

if TYPE_CHECKING:
    from main import Main
    from pandas import DataFrame


class HomeTab:
    DEFAULT_FARM_ID: str = ""

    def __init__(self, main, tab: DeltaGenerator) -> None:
        self.main: Main = main
        self.tab: DeltaGenerator = tab
        self.farm_id: str = ""
        self.create_tab()

    def get_farm_id(self) -> str:
        return self.farm_id

    def create_tab(self) -> None:
        # Get farm ID from query parameters
        app_state: dict[str, list[str]] = st.experimental_get_query_params()
        default_farm_id: str = app_state.get("farm", [self.DEFAULT_FARM_ID])[0]

        self.tab.markdown("##### 🔻 SEARCH FARM ID 🔻")

        col: DeltaGenerator
        buff: DeltaGenerator
        col, buff = self.tab.columns([2, 4.5])

        col_search2: DeltaGenerator
        col_ok2: DeltaGenerator
        col_search2, col_ok2 = col.columns([2, 2])
        farm_id: str = col_search2.text_input(
            "write your farm ID",
            max_chars=6,
            key="farm-input",
            label_visibility="collapsed",
            value=default_farm_id,
        )
        self.farm_id = farm_id
        buttonok: bool = col_ok2.button("OK", key="home_ok_btn")

        self.ft_cons: dict[str, DeltaGenerator] = {}
        self.bt_cons: dict[str, DeltaGenerator] = {}
        self.worth_cons: dict[str, DeltaGenerator] = {}

        status_ok: DeltaGenerator = self.tab.container()
        # def load_farm(self) -> None:
        if not buttonok:
            return
        farm_tab: DeltaGenerator
        bumpkin_tab: DeltaGenerator
        worth_tab: DeltaGenerator
        farm_tab, bumpkin_tab, worth_tab = self.tab.tabs(
            ["🏡FARM ", "👨‍🌾BUMPKIN ", "💎WORTH "]
        )

        self.ft_cons = self.create_farm_tab(farm_tab)
        self.bt_cons = self.create_bp_tab(bumpkin_tab)
        self.worth_cons = self.create_worth_tab(worth_tab)

        app_state: dict[str, list[str]] = st.experimental_get_query_params()
        app_state["farm"] = [self.farm_id]
        url: str = f"https://api.sunflower-land.com/visit/{self.farm_id}"
        # url: str = f"https://api.sunflower-land.com/visit/137396"
        st.experimental_set_query_params(**app_state)

        response: requests.Response = requests.get(url)
        if response.status_code == 429:
            status_ok.error(
                "Error: Too many requests, please try again in a few seconds"
            )
            return
        elif response.status_code == 404:
            status_ok.error(
                "Error 404: Make sure you are writing a valid "
                + "Farm ID with only numbers"
            )
            return
        elif response.status_code != 200:
            status_ok.error(f"Error: {response.status_code}")
            return

        status_ok.success(f" ✅ Done! Farm {self.farm_id} loaded.")

        # buildings_dict = "Workbench:{}, Water Well:{}, Kitchen:{}, Tent:{},
        # Hen House:{}, Hen House2:{}, Bakery:{}, Smoothie Shack:{}, Deli:{},
        # Warehouse:{}, Toolshed:{}"
        building_items: list[str] = [
            "Toolshed",
            "Warehouse",
            "Deli",
            "Smoothie Shack",
            "Bakery",
            "Hen House2",
            "Hen House",
            "Tent",
            "Kitchen",
            "Water Well",
        ]
        building_items_resources: dict[str, dict[str, int | float]] = {
            "Toolshed": {
                "Wood": 500,
                "Iron": 30,
                "Gold": 25,
                "Axe": 100,
                "Pickaxe": 50,
            },
            "Warehouse": {
                "Wood": 250,
                "Stone": 150,
                "Potato": 5000,
                "Pumpkin": 2000,
                "Wheat": 500,
                "Kale": 100,
            },
            "Deli": {"Wood": 50, "Stone": 50, "Gold": 10, "SFL": 3.75},
            "Smoothie Shack": {"Wood": 25, "Stone": 25, "Iron": 10},
            "Bakery": {"Wood": 50, "Stone": 20, "Gold": 5, "SFL": 2.5},
            "Hen House2": {
                "Egg": 300,
                "Wood": 200,
                "Iron": 15,
                "Gold": 15,
                "SFL": 10,
            },
            "Hen House": {
                "Wood": 30,
                "Iron": 5,
                "Gold": 5,
                "SFL": 1.25,
            },
            "Tent": {"Wood": 50, "SFL": 0.0625},
            "Kitchen": {"Wood": 30, "Stone": 5, "SFL": 0.125},
            "Water Well": {"Wood": 5, "Stone": 5, "SFL": 1},
        }

        wood_price_converted: Decimal = self.main.priceAPI.get_resource_price(
            601
        )
        stone_price_converted: Decimal = self.main.priceAPI.get_resource_price(
            602
        )
        iron_price_converted: Decimal = self.main.priceAPI.get_resource_price(
            603
        )
        gold_price_converted: Decimal = self.main.priceAPI.get_resource_price(
            604
        )
        egg_price_converted: Decimal = self.main.priceAPI.get_resource_price(
            605
        )

        resources_items: list[str] = [
            "Gold",
            "Iron",
            "Stone",
            "Wood",
            "Egg",
        ]

        with open("data/expansions.json", "r", encoding="utf-8") as f:
            expansions: dict[str, dict[str, int]] = json.load(f)

        with open("data/expansion_costs.json", "r", encoding="utf-8") as f:
            expansions_cost: dict[str, dict] = json.load(f)

        helios_sfl: dict[str, float] = {
            "Cactus": 0.25,
            " Basic Bear": 0.625,
            "Potted Potato": 0.625,
            "Potted Pumpkin": 2.5,
            "Potted Sunflower": 0.25,
            "White Tulips": 0.25,
            "Dirt Path": 0.625,
        }

        nft_resources: dict[str, dict[str, float | int]] = {
            "Immortal Pear": {"SFL": 3.4375, "Gold": 5},
            "Treasure Map": {"Gold": 5, "SFL": 1.64},
            "Fence": {"SFL": 0.125, "Wood": 5},
            "Bush": {"SFL": 1.25, "Wood": 5},
            "Shrub": {"SFL": 0.625, "Wood": 3},
        }

        mutant_items: set[str] = {
            "Rich Chicken",
            "Fat Chicken",
            "Speed Chicken",
            "Ayam Cemani",
        }

        crop_items: set[str] = {
            "Sunflower",
            "Potato",
            "Pumpkin",
            "Carrot",
            "Cabbage",
            "Beetroot",
            "Cauliflower",
            "Parsnip",
            "Eggplant",
            "Radish",
            "Wheat",
            "Kale",
        }
        crop_price: dict[str, float] = {
            "Sunflower": 0.000125,
            "Potato": 0.000875,
            "Pumpkin": 0.0025,
            "Carrot": 0.005,
            "Cabbage": 0.0094,
            "Beetroot": 0.0175,
            "Cauliflower": 0.0265,
            "Parsnip": 0.0405,
            "Eggplant": 0.05,
            "Radish": 0.0595,
            "Wheat": 0.044,
            "Kale": 0.0625,
        }
        bounty_items: set[str] = {
            "Crab",
            "Old Bottle",
            "Sea Cucumber",
            "Seaweed",
            "Starfish",
            "Wooden Compass",
            "Iron Compass",
            "Pipi",
            "Clam Shell",
            "Coral",
            "Pearl",
            "Pirate Bounty",
        }
        bounty_price: dict[str, float] = {
            "Crab": 0.09375,
            "Old Bottle": 0.140625,
            "Sea Cucumber": 0.140625,
            "Seaweed": 0.46875,
            "Starfish": 0.703125,
            "Wooden Compass": 0.8203125,
            "Iron Compass": 1.171875,
            "Pipi": 1.171875,
            "Clam Shell": 2.34375,
            "Coral": 9.375,
            "Pearl": 23.4375,
            "Pirate Bounty": 46.875,
        }
        tool_items: set[str] = {
            "Axe",
            "Pickaxe",
            "Stone Pickaxe",
            "Iron Pickaxe",
            "Rusty Shovel",
            "Sand Shovel",
            "Sand Drill",
        }
        tool_price: dict[str, float] = {
            "Axe": 0.0625,
            "Pickaxe": 0.0625,
            "Stone Pickaxe": 0.0625,
            "Iron Pickaxe": 0.25,
            "Rusty Shovel": 0.0625,
            "Sand Shovel": 0.0625,
            "Sand Drill": 0.125,
        }
        food_items: set[str] = {
            "Mashed Potato",
            "Pumpkin Soup",
            "Bumpkin Broth",
            "Boiled Eggs",
            "Kale Stew",
            "Mushroom Soup",
            "Reindeer Carrot",
            "Kale Omelette",
            "Cabbers n Mash",
            "Roast Veggies",
            "Bumpkin Salad",
            "Goblin's Treat",
            "Cauliflower Burger",
            "Pancakes",
            "Club Sandwich",
            "Mushroom Jacket Potatoes",
            "Sunflower Crunch",
            "Bumpkin Roast",
            "Goblin Brunch",
            "Fruit Salad",
            "Sunflower Cake",
            "Potato Cake",
            "Pumpkin Cake",
            "Carrot Cake",
            "Cabbage Cake",
            "Beetroot Cake",
            "Cauliflower Cake",
            "Parsnip Cake",
            "Radish Cake",
            "Wheat Cake",
            "Apple Pie",
            "Honey Cake",
            "Orange Cake",
            "Apple Juice",
            "Orange Juice",
            "Purple Smoothie",
            "Power Smoothie",
            "Bumpkin Detox",
            "Pirate Cake",
        }
        food_deli_items: set[str] = {
            "Blueberry Jam",
            "Fermented Carrots",
            "Sauerkraut",
            "Fancy Fries",
        }
        food_xp: dict[str, int] = {
            "Mashed Potato": 3,
            "Pumpkin Soup": 24,
            "Bumpkin Broth": 96,
            "Boiled Eggs": 90,
            "Kale Stew": 400,
            "Mushroom Soup": 56,
            "Reindeer Carrot": 10,
            "Kale Omelette": 1250,
            "Cabbers n Mash": 250,
            "Roast Veggies": 170,
            "Bumpkin Salad": 290,
            "Goblin's Treat": 500,
            "Cauliflower Burger": 255,
            "Pancakes": 480,
            "Club Sandwich": 170,
            "Mushroom Jacket Potatoes": 240,
            "Sunflower Crunch": 50,
            "Bumpkin Roast": 2500,
            "Goblin Brunch": 2500,
            "Fruit Salad": 225,
            "Sunflower Cake": 525,
            "Potato Cake": 650,
            "Pumpkin Cake": 625,
            "Carrot Cake": 750,
            "Cabbage Cake": 860,
            "Beetroot Cake": 1250,
            "Cauliflower Cake": 1190,
            "Parsnip Cake": 1300,
            "Radish Cake": 1200,
            "Wheat Cake": 1100,
            "Apple Pie": 720,
            "Honey Cake": 760,
            "Orange Cake": 730,
            "Apple Juice": 500,
            "Orange Juice": 375,
            "Purple Smoothie": 310,
            "Power Smoothie": 775,
            "Bumpkin Detox": 975,
            "Pirate Cake": 3000,
        }
        food_deli_xp: dict[str, int] = {
            "Blueberry Jam": 380,
            "Fermented Carrots": 250,
            "Sauerkraut": 500,
            "Fancy Fries": 1000,
        }

        cake_and_pie_items: set[str] = {
            "Sunflower Cake",
            "Potato Cake",
            "Pumpkin Cake",
            "Carrot Cake",
            "Cabbage Cake",
            "Beetroot Cake",
            "Cauliflower Cake",
            "Parsnip Cake",
            "Radish Cake",
            "Wheat Cake",
            "Apple Pie",
            "Honey Cake",
            "Orange Cake",
            "Pirate Cake",
        }

        fruits: set[str] = {"Apple", "Blueberry", "Orange"}
        # for item in food_items:
        #    if "Cake" in item or "Pie" in item:
        #        cake_and_pie_items[item] = None

        crop_data = {}
        inventory_dict = {}
        skills_dict = {}
        equipped_dict = {}
        buildings_dict = {}

        food_quantity: dict[str, int] = {
            item: 0 for item in food_items.union(food_deli_items)
        }
        crop_quantity: dict[str, int] = {item: 0 for item in crop_items}
        fruit_quantity: dict[str, int] = {item: 0 for item in fruits}
        bounty_quantity: dict[str, int] = {item: 0 for item in bounty_items}
        tool_quantity: dict[str, int] = {item: 0 for item in tool_items}
        mutant_quantity: dict[str, int] = {item: 0 for item in mutant_items}

        baloon_items: set[str] = {
            "Gold",
            "Iron",
            "Stone",
            "Wood",
            "Egg",
        }
        baloon_inv = {}
        baloon_quantity = {}
        total_inv_value = 0
        buildings_farm = {}
        buildings_farm_price = {}

        # Define a function to calculate the price of a building
        def get_building_price(building_name) -> Decimal:
            building = building_items_resources.get(building_name)
            if not building:
                return Decimal(0)
            total_price = Decimal(0)
            for item in building:
                if item in crop_price:
                    total_price += Decimal(crop_price[item]) * Decimal(
                        building[item]
                    )
                elif item in tool_price:
                    total_price += Decimal(tool_price[item]) * Decimal(
                        building[item]
                    )
                elif item in resources_items:
                    if item == "Wood":
                        total_price += Decimal(wood_price_converted) * Decimal(
                            building[item]
                        )
                    elif item == "Stone":
                        total_price += Decimal(stone_price_converted) * Decimal(
                            building[item]
                        )
                    elif item == "Iron":
                        total_price += Decimal(iron_price_converted) * Decimal(
                            building[item]
                        )
                    elif item == "Gold":
                        total_price += Decimal(gold_price_converted) * Decimal(
                            building[item]
                        )
                    elif item == "Egg":
                        egg_price: Decimal = (
                            self.main.priceAPI.get_resource_price(605)
                        )
                        total_price += Decimal(egg_price) * Decimal(
                            building[item]
                        )
                elif item == "SFL":
                    total_price += Decimal(building[item])
            return total_price

        # Define a function to calculate the price of an expansion
        def get_expansion_price(current_resources) -> Decimal:
            total_price_exp = Decimal(0)
            for item, quantity in current_resources.items():
                if item in resources_items:
                    if item == "Wood":
                        total_price_exp += Decimal(
                            wood_price_converted
                        ) * Decimal(quantity)
                    elif item == "Stone":
                        total_price_exp += Decimal(
                            stone_price_converted
                        ) * Decimal(quantity)
                    elif item == "Iron":
                        total_price_exp += Decimal(
                            iron_price_converted
                        ) * Decimal(quantity)
                    elif item == "Gold":
                        total_price_exp += Decimal(
                            gold_price_converted
                        ) * Decimal(quantity)
            return total_price_exp

        data: dict[str, dict] = response.json()
        state: dict[str, dict | float] = data.get("state", {})

        balance_get: dict | float | str = state.get("balance", "0.0")
        assert isinstance(balance_get, str)
        balance_sfl: float = round(float(balance_get), 2)
        if balance_sfl < 10:
            withdraw: float = balance_sfl - (0.3 * balance_sfl)
        elif balance_sfl < 100:
            withdraw: float = balance_sfl - (0.25 * balance_sfl)
        elif balance_sfl < 1000:
            withdraw: float = balance_sfl - (0.2 * balance_sfl)
        elif balance_sfl < 5000:
            withdraw: float = balance_sfl - (0.15 * balance_sfl)
        else:
            withdraw: float = balance_sfl - (0.1 * balance_sfl)
        withdraw_usd: float = withdraw * self.main.sfl_price
        withdraw_usd_str: str = "{:.2f}".format(round(withdraw_usd, 2))

        balance: dict | float | str = state.get("balance", 0.0)
        prevbalance: dict | float | str = state.get("previousBalance", 0.0)
        assert isinstance(balance, str) and isinstance(prevbalance, str)
        balance_float = float(balance)
        prevbalance_float = float(prevbalance)
        daily_limit: float = balance_float - prevbalance_float
        inventory_dict: dict | float | None = state.get("inventory")
        assert isinstance(inventory_dict, dict)
        # inventory_dict = eval(str(inventory))
        buildings_dict: dict | float | None = state.get("buildings")
        assert isinstance(buildings_dict, dict)
        # buildings_dict = eval(str(buildings_str))

        db: dict | float = state.get("dawnBreaker", {})
        assert isinstance(db, dict)
        laternsWeek: dict[str, int] = db.get("lanternsCraftedByWeek", {})
        week1: int = laternsWeek.get("1", 0)
        week2: int = laternsWeek.get("2", 0)
        week3: int = laternsWeek.get("3", 0)
        week4: int = laternsWeek.get("4", 0)
        week5: int = laternsWeek.get("5", 0)
        week6: int = laternsWeek.get("6", 0)
        week7: int = laternsWeek.get("7", 0)
        week8: int = laternsWeek.get("8", 0)

        traveller: dict = db.get("traveller", {})
        traveller_count = 0
        if traveller:
            traveller_count: int = traveller.get("discoveredCount", 0)

        answered_riddle_ids: dict[str, str] = db.get("answeredRiddleIds", {})
        riddle_week_map: dict[str, int] = {
            "hoot-dawn-breaker-week-1": week1,
            "hoot-dawn-breaker-week-2": week2,
            "hoot-dawn-breaker-week-3": week3,
            "hoot-dawn-breaker-week-4": week4,
            "hoot-dawn-breaker-week-5": week5,
            "hoot-dawn-breaker-week-6": week6,
            "hoot-dawn-breaker-week-7": week7,
            "hoot-dawn-breaker-week-8": week8,
        }

        bumpkin: dict | float | None = state.get("bumpkin", None)
        taskcount = 0
        count_chore = 0

        skip_chores = 0
        completed_chore = 0
        requirement_chore = 0
        description_chore = ""
        ticket_chore = 0
        if isinstance(bumpkin, dict):
            skills_dict: dict[str, int] = bumpkin.get("skills", {})
            # skills_dict = eval(str(skills))
            equipped_dict: dict[str, str] = bumpkin.get("equipped", {})
            # equipped_dict = eval(str(equipped))
            activity: dict[str, int] = bumpkin.get("activity", {})

            hayseed: dict | float = state.get("hayseedHank", {})
            assert isinstance(hayseed, dict)
            completed_chore: int = hayseed.get("dawnBreakerChoresCompleted", 0)
            skip_chores: int = hayseed.get("dawnBreakerChoresSkipped", 0)
            chore: dict = hayseed.get("chore", {})
            progress_chore: dict = hayseed.get("progress", {})
            if progress_chore is None:
                count_chore = 0  # Or whatever default value you want to use
            else:
                count_chore: int = progress_chore.get("startCount", 0)
            activitytask: str = chore.get("activity", "N/A")
            description_chore: str = chore.get("description", "N/A")
            reward_chore: dict = chore.get("reward", {})
            requirement_chore: int = chore.get("requirement", 0)
            item_chore: dict = reward_chore.get("items", {})
            ticket_chore: int = item_chore.get("Dawn Breaker Ticket", 0)
            taskcount: int = activity.get(activitytask, 0)

        total_xp = 0
        for item, quantity in inventory_dict.items():
            if item not in food_xp and item not in food_deli_xp:
                continue
            if item in food_items:
                xp = int(food_xp[item])
                total_xp += xp * int(quantity)
                # Update the quantity of the food item
                food_quantity[item] += int(quantity)
            elif item in food_deli_items:
                xp = int(food_deli_xp[item])
                if "Curer" in skills_dict:
                    xp *= 1.15
                total_xp += xp * int(quantity)
                # Update the quantity of the food deli item
                food_quantity[item] += int(quantity)

        if "Kitchen Hand" in skills_dict:
            total_xp *= 1.05
        if "Observatory" in inventory_dict:
            total_xp *= 1.05
        if "Golden Spatula" in equipped_dict.values():
            total_xp *= 1.10

        crop_sells = 0.0
        for item, quantity in inventory_dict.items():
            if item not in crop_price:
                continue
            if item in crop_items:
                c_price = crop_price[item]
                crop_sells += round(float(quantity)) * c_price
                crop_quantity[item] += round(float(quantity))

        fruit_sells = 0.0
        for item, quantity in inventory_dict.items():
            if item not in self.main.fruits_price:
                continue
            if item in fruits:
                f_price: float = self.main.fruits_price[item]
                fruit_sells += round(float(quantity)) * f_price
                fruit_quantity[item] += round(float(quantity))

        if "Green Thumb" in inventory_dict:
            crop_sells *= 1.05

        bounty_sells = 0.0
        for item, quantity in inventory_dict.items():
            if item not in bounty_price:
                continue
            if item in bounty_items:
                b_price: float = bounty_price[item]
                bounty_sells += int(quantity) * b_price
                bounty_quantity[item] += int(quantity)

        if "Treasure Map" in inventory_dict:
            bounty_sells *= 1.20

        tool_cost = 0
        for item, quantity in inventory_dict.items():
            if item not in tool_price:
                continue
            if item in tool_items:
                t_price: float = tool_price[item]
                tool_cost += int(float(quantity)) * t_price
                tool_quantity[item] += int(float(quantity))

        chickens: dict | float = state.get("chickens", {})
        if isinstance(chickens, dict):
            chickens_str = str(chickens)
            chickens_dict: dict | float = state["chickens"]

            if isinstance(chickens_dict, dict):
                for chicken in chickens_dict.values():
                    if "reward" in chicken:
                        for item in chicken["reward"]["items"]:
                            if item["name"] in mutant_items:
                                mutant_quantity[item["name"]] += item["amount"]

        resources: list[str] = [
            "crops",
            "trees",
            "stones",
            "iron",
            "gold",
            "fruitPatches",
        ]
        totals = {}
        total_resources = totals

        for resource in resources:
            value = state.get(resource)
            if value is not None:
                total: int = str(value).count("createdAt")
            else:
                total = 0
            totals[resource] = total

        crops_str = state.get("crops")
        crops_dict = eval(str(crops_str))

        dawn_breaker_tickets_count = 0
        for crop_id, crop_info in crops_dict.items():
            if "crop" in crop_info:
                crop_name = crop_info["crop"]["name"]
                crop_amount = crop_info["crop"]["amount"]
                if "reward" in crop_info["crop"]:
                    reward_items = crop_info["crop"]["reward"]["items"]
                    for reward_item in reward_items:
                        if reward_item["name"] == "Dawn Breaker Ticket":
                            dawn_breaker_tickets_count += reward_item["amount"]
                if crop_name in crop_data:
                    crop_data[crop_name]["mentions"] += 1
                    crop_data[crop_name]["amount"] += crop_amount
                else:
                    crop_data[crop_name] = {
                        "mentions": 1,
                        "amount": crop_amount,
                    }
            else:
                continue

        state_json: dict = response.json().get("state", {})

        num_wood: int = sum(
            1 for tree in state_json.get("trees", {}).values() if "wood" in tree
        )
        total_wood_amount: int = sum(
            tree.get("wood", {}).get("amount", 0)
            for tree in state_json.get("trees", {}).values()
        )

        num_stones: int = sum(
            1
            for stone in state_json.get("stones", {}).values()
            if "stone" in stone
        )
        total_stone_amount: int = sum(
            stone.get("stone", {}).get("amount", 0)
            for stone in state_json.get("stones", {}).values()
        )

        num_iron: int = sum(
            1 for iron in state_json.get("iron", {}).values() if "stone" in iron
        )
        total_iron_amount: int = sum(
            iron.get("stone", {}).get("amount", 0)
            for iron in state_json.get("iron", {}).values()
        )

        num_gold: int = sum(
            1 for gold in state_json.get("gold", {}).values() if "stone" in gold
        )
        total_gold_amount: int = sum(
            gold.get("stone", {}).get("amount", 0)
            for gold in state_json.get("gold", {}).values()
        )

        num_chickens: int = sum(
            1
            for chicken in state_json.get("chickens", {}).values()
            if "fedAt" in chicken
        )
        total_chickens_amount: int = sum(
            chicken.get("multiplier", 0)
            for chicken in state_json.get("chickens", {}).values()
            if "fedAt" in chicken
        )
        delivery: dict | float = state.get("delivery", {})
        if isinstance(delivery, dict):
            deliveryTotal: int = delivery.get("fulfilledCount", 0)
            delivery_data: list[dict] = delivery.get("orders", [])
            treasureIsland: dict | float = state.get("treasureIsland", {})
        else:
            delivery_data = []
            deliveryTotal = 0
            treasureIsland = {}

        bumpkin = state.get("bumpkin")
        if not bumpkin or not isinstance(bumpkin, dict):
            bumpkin = {}
        bump_xp: float = bumpkin.get("experience", 0.0)
        bump_id: int = bumpkin.get("id", 0)
        bump_achi: dict = bumpkin.get("achievements", {})
        bump_url: str = bumpkin.get("tokenUri", "")
        activities: dict = bumpkin.get("activity", {})
        trees_chopped: int = activities.get("Tree Chopped", 0)
        egg_collected: int = activities.get("Egg Collected", 0)
        sfl_earn: float = activities.get("SFL Earned", 0.0)
        sfl_spent: float = activities.get("SFL Spent", 0.0)
        sandshovel: int = activities.get("Treasure Dug", 0)
        drill: int = activities.get("Treasure Drilled", 0)
        if sandshovel is not None and drill is not None:
            dug_holes: int = sandshovel + drill
        else:
            dug_holes = 0

        fed_activities: dict = {}
        dug_activities: dict = {}
        cooked_activities: dict = {}
        harvested_activities: dict = {}
        harvested_fruit_activities: set = {
            "Apple Harvested",
            "Blueberry Harvested",
            "Orange Harvested",
        }
        mined_activities: dict = {}
        fed_total = 0
        cooked_total = 0
        harvested_total = 0
        fruit_total = 0

        for activity, value in activities.items():
            if "Fed" in activity:
                fed_activities[activity] = value
                fed_total += value
            if "Dug" in activity:
                if activity not in ["Treasure Dug"]:
                    dug_activities[activity] = value
            if "Cooked" in activity:
                cooked_activities[activity] = value
                cooked_total += value
            if "Mined" in activity:
                mined_activities[activity] = value
            if "Harvested" in activity:
                harvested_activities[activity] = value
                if activity not in harvested_fruit_activities:
                    harvested_total += value
                else:
                    fruit_total += value

        fruit_patches_str = state.get("fruitPatches")
        if isinstance(fruit_patches_str, str):
            fruit_patches_dict: dict = json.loads(fruit_patches_str)
        else:
            assert isinstance(fruit_patches_str, dict)
            fruit_patches_dict = fruit_patches_str
        fruit: dict[str, list] = {}

        self.ft_cons["balance_check"].info(
            f"📈 SFL Current Price: **${self.main.sfl_price:.4f}**"
        )
        # balance_check.info(f"\n
        # 🟣 MATIC Current Price: **${matic_price:.2f}**")
        self.ft_cons["balance_check"].write(
            f" - 💰 SFL Balance: **:green[{balance_sfl:.2f}]**"
        )
        self.ft_cons["balance_check"].write(
            f" - 💸 SFL After Withdraw: **:red[{withdraw:.2f}]**"
        )
        self.ft_cons["balance_check"].write("\n")
        self.ft_cons["balance_check"].success(
            f"\n💱 Withdraw in Dolars: **${withdraw_usd_str}**"
        )

        self.ft_cons["hoarder"].info(
            "\n \U0001F4B0  **SFL Hoarder Limit: [{:.2f} / 255]**".format(
                daily_limit
            )
        )
        # hoarder.warning("\n **Have in mind that apart of the SFL Hoarder
        # Limit, there is also the SFL Daily Limit of 250, that is not going
        # to let you sync again if you go over it, this daily limit restarts
        # everyday at 00:00 UTC.**")
        spend_info_written = False

        for item in self.main.inventory_items:
            inv: dict[str, str] | float = state.get("inventory", {})
            old_inv: dict[str, str] | float = state.get("previousInventory", {})
            assert isinstance(inv, dict)
            assert isinstance(old_inv, dict)
            new_item: str = inv.get(item, "0")
            old_item: str = old_inv.get(item, "0")
            if new_item is not None:
                if old_inv is None:
                    diff = int(round(float(new_item)))
                else:
                    diff: int = int(round(float(new_item))) - int(
                        round(float(old_item))
                    )
                if diff != 0:
                    limit: int = self.main.limits.get(item, 0)
                    if isinstance(diff, str) and diff.isnumeric():
                        diff = int(diff)
                    if isinstance(limit, str) and limit.isnumeric():
                        limit = int(limit)
                    if limit != 0:
                        percentage: float = (diff / limit) * 100
                        if percentage < 0:
                            percentage = 0
                        percentage_float = float(percentage)
                        percentage_number: str = "{:.0f}".format(
                            percentage_float
                        )
                        percentage_final: float = float(percentage_number) / 100

                        if percentage > 0:
                            self.ft_cons["hoarder"].write(
                                f" -{self.main.emojis.get(item)} "
                                + f"{item.capitalize()}: [{diff} / "
                                + f"{self.main.limits.get(item)}] = "
                                + f"**{percentage_number}%**"
                            )
                            if percentage_final > 1:
                                percentage_final = 1.0
                            self.ft_cons["hoarder"].progress(
                                percentage_final, text=None
                            )
                        else:
                            if not spend_info_written:
                                self.ft_cons["spend"].info(
                                    "\n ⚠️ **Negative values means that you "
                                    + "spent more of that resource of what you "
                                    + "gather/harvest since your last SYNC.**"
                                )
                                spend_info_written = True
                            self.ft_cons["spend"].write(
                                f" -{self.main.emojis.get(item)} "
                                + f"{item.capitalize()}: [{diff} / "
                                + f"{self.main.limits.get(item)}]"
                            )
                    else:
                        continue

        total_mutant = sum(mutant_quantity.values())
        if total_mutant == 0:
            self.ft_cons["c_mutant"].info("\n 🐣 **Mutants Drop: 0**")
        else:
            self.ft_cons["c_mutant"].info(
                f"\n 🐣 **Mutants Drop: {total_mutant}**"
            )
            for item in mutant_items:
                if mutant_quantity[item] > 0:
                    self.ft_cons["c_mutant"].success(
                        f"\n 🐤 **{item}: {mutant_quantity[item]}**"
                    )

        for item in baloon_items:
            inv = state.get("inventory", {})
            assert isinstance(inv, dict)
            new_inv_baloon: str | None = inv.get(item, None)
            if new_inv_baloon is not None:
                baloon_inv[item] = new_inv_baloon
                baloon_quantity[item] = Decimal(new_inv_baloon)

        wood_inv_value: Decimal = (
            baloon_quantity.get("Wood", 0) * wood_price_converted
        )
        stone_inv_value: Decimal = (
            baloon_quantity.get("Stone", 0) * stone_price_converted
        )
        iron_inv_value: Decimal = (
            baloon_quantity.get("Iron", 0) * iron_price_converted
        )
        gold_inv_value: Decimal = (
            baloon_quantity.get("Gold", 0) * gold_price_converted
        )
        egg_inv_value: Decimal = (
            baloon_quantity.get("Egg", 0) * egg_price_converted
        )

        total_npc_market = crop_sells + fruit_sells + bounty_sells
        total_npc_market_usd: Decimal = Decimal(total_npc_market) * Decimal(
            self.main.sfl_price
        )
        total_baloon_market = (
            egg_inv_value
            + wood_inv_value
            + stone_inv_value
            + iron_inv_value
            + gold_inv_value
        )
        total_sales: Decimal = Decimal(total_npc_market) + Decimal(
            total_baloon_market
        )
        total_sales_usd: Decimal = Decimal(total_sales) * Decimal(
            self.main.sfl_price
        )
        total_baloon_market_usd: Decimal = Decimal(
            total_baloon_market
        ) * Decimal(self.main.sfl_price)

        self.ft_cons["farm_info"].info(f"\n 🌱 **Crops to be Harvest:**")
        for crop_name, info in crop_data.items():
            final_amount = round(info["amount"], 2)
            emoji = self.main.emojis.get(crop_name, "")
            self.ft_cons["farm_info"].write(
                f" - {emoji} **{final_amount:.2f} {crop_name}** — "
                + f"{info['mentions']}x Plots"
            )
        if dawn_breaker_tickets_count > 0:
            self.ft_cons["farm_info"].write(
                f"- 🎟️ **{dawn_breaker_tickets_count} Dawn Breaker Ticket**"
            )

        self.ft_cons["farm_info"].write("\n")
        self.ft_cons["farm_info"].success(
            f"\n ⚒️ **Resources to be Gathered:**"
        )
        self.ft_cons["farm_info"].write(
            f" - 🌲 **{total_wood_amount:.2f} Wood** — {num_wood}x Trees"
        )
        self.ft_cons["farm_info"].write(
            f" - ⚪ **{total_stone_amount:.2f} Stone** — {num_stones}x Stones"
        )
        self.ft_cons["farm_info"].write(
            f" - 🟠 **{total_iron_amount:.2f} Iron** — {num_iron}x Iron Rocks"
        )
        self.ft_cons["farm_info"].write(
            f" - 🟡 **{total_gold_amount:.2f} Gold** — {num_gold}x Gold Rocks"
        )
        self.ft_cons["farm_info"].write(
            f" - 🥚 **{total_chickens_amount:.2f} Eggs** — "
            + f"{num_chickens}x Chickens"
        )

        # farm_info.write("\n")
        # farm_info.success(f"\n 📊 **Total Nodes:**")
        # farm_info.write(f"\n - 🌱 **Plots: {totals['crops']}** -
        # ⚪ **Stone: {totals['stones']}**")
        # farm_info.write(f"\n - 🌲 **Trees: {totals['trees']}** -
        #   🟠 **Iron: {totals['iron']}**")
        # farm_info.write(f"\n - 🍒 **Fruit: {totals['fruitPatches']}** ---
        #   🟡 **Gold: {totals['gold']}**")

        lantern_name: dict[int, str] = {
            1: "Luminous",
            2: "Radiance",
            3: "Aurora",
            4: "Radiance",
            5: "Aurora",
            6: "Luminous",
            7: "Ocean",
            8: "Solar",
        }

        riddle_reward: dict[int, str] = {
            1: "---",
            2: "50",
            3: "75",
            4: "50",
            5: "50",
            6: "50",
            7: "50",
            8: "100",
        }

        # dawn_breaker.write("\n")
        # dawn_breaker.info(f" 👨‍🌾 **HaySeed Hank:**")

        # Define progress_count with default value of 0
        progress_count = 0

        # Check if taskcount and count_chore are not None
        if taskcount is not None and count_chore is not None:
            progress_count = taskcount - count_chore

        if bumpkin:
            df_weeks: list = []
            for week in range(1, 9):
                lanterns: int = laternsWeek.get(str(week), 0)
                if week == 1:
                    riddle = "-----"
                else:
                    riddle: str = (
                        "Yes ✅"
                        if f"hoot-dawn-breaker-week-{week}"
                        in answered_riddle_ids
                        else "No ❌"
                    )
                lantern_name_value: str = lantern_name.get(week, "")
                if lanterns > 0:
                    lanterns_info: str = f"{lanterns} {lantern_name_value}"
                else:
                    lanterns_info = ""
                df_weeks.append(
                    {
                        "Week": week,
                        "Lanterns Crafted": lanterns_info,
                        "Riddle Solved": riddle,
                        "Reward 🎟️": riddle_reward.get(week, ""),
                    }
                )

            dfweek = pd.DataFrame(df_weeks)
            dfweek: DataFrame = dfweek[
                dfweek["Lanterns Crafted"] != ""
            ]  # Drop rows with empty "Lanterns Crafted" column
            dfweek.set_index("Week", inplace=True)
            self.ft_cons["dawn_breaker"].write(dfweek)
            if skip_chores is None:
                skip_chores = 0
            if completed_chore is None:
                completed_chore = 0

            if completed_chore < (125 - skip_chores):
                next_loop: int | None = 125 - completed_chore - skip_chores
            elif completed_chore < (183 - skip_chores):
                next_loop = 183 - completed_chore - skip_chores
            elif completed_chore < (241 - skip_chores):
                next_loop = 241 - completed_chore - skip_chores
            elif completed_chore < (299 - skip_chores):
                next_loop = 299 - completed_chore - skip_chores
            elif completed_chore < (357 - skip_chores):
                next_loop = 357 - completed_chore - skip_chores
            elif completed_chore < (415 - skip_chores):
                next_loop = 415 - completed_chore - skip_chores
            elif completed_chore < (473 - skip_chores):
                next_loop = 473 - completed_chore - skip_chores
            else:
                next_loop = None

            first_traveller = 1689170400
            respawn_interval: timedelta = timedelta(hours=24)
            current_time2: float = datetime.now().timestamp()
            traveller_event: float = (
                current_time2 - first_traveller
            ) / respawn_interval.total_seconds()
            traveller_day: int = int(traveller_event + 1)

            self.ft_cons["wanderleaf"].info(
                f" 📆 Days since the Event start: **{traveller_day:.0f}**"
            )
            self.ft_cons["wanderleaf"].success(
                f" 🎟️ Claimed Tickets: **{traveller_count}/13**"
            )

            self.ft_cons["dawn_breaker"].info(
                f" 🗂️ Current Quest: **{description_chore}**"
            )
            self.ft_cons["dawn_breaker"].write(
                f" - 🎟️ Tickets Reward: **{ticket_chore}**"
            )
            self.ft_cons["dawn_breaker"].write(
                f" - ⏳ Progress: **{progress_count} of {requirement_chore}**"
            )
            self.ft_cons["dawn_breaker"].write("\n")
            if next_loop is not None:
                self.ft_cons["dawn_breaker"].success(
                    f"\n 📊 **Total Quest Completed: {completed_chore}** "
                    + f"(Next Loop in: **{next_loop})**"
                )
            else:
                self.ft_cons["dawn_breaker"].success(
                    f"\n 📊 **Total Quest Completed: {completed_chore}**"
                )
        else:
            self.ft_cons["dawn_breaker"].error(
                f" **There aren't Bumpkins in this Farm.**"
            )

        deliveryNpcList = []
        deliveryItemList: list = []
        deliveryRewardList: list = []
        deliveryTimeList: list = []

        ddata: list = []
        if delivery_data:
            for order in delivery_data:
                npc = order["from"]
                items = order["items"]
                reward = order["reward"]
                readytime = order["readyAt"]

                if npc:
                    deliveryNpcList.append(npc)

                if items:
                    deliveryItemList.extend(list(items.keys()))

                if reward and "items" in reward:
                    reward_items: dict = reward["items"]
                    if reward_items:
                        deliveryRewardList.extend(list(reward_items.keys()))

                if readytime:
                    deliveryTimeList.append(readytime)

            current_time: float = (
                datetime.now().timestamp() * 1000
            )  # Convert to milliseconds

            for index, order in enumerate(delivery_data, start=1):
                npc = order.get("from")
                items: dict = order.get("items", {})
                reward: dict = order.get("reward", {})
                readytime: int = order.get("readyAt", int)

                if npc:
                    npc_name = order["from"]
                    if npc_name and "pumpkin' pete" in npc_name:
                        npc_name = f"pete"
                        deliveryNpc = npc_name.capitalize()
                    else:
                        deliveryNpc = npc_name.capitalize()
                else:
                    deliveryNpc = ""

                if items:
                    deliveryItems: str = ", ".join(items.keys())
                    deliveryItems_value: str = ", ".join(
                        [f"{value}x {key}" for key, value in items.items()]
                    )
                else:
                    deliveryItems = ""
                    deliveryItems_value = ""
                if reward and "sfl" in reward:
                    reward_sfl = reward["sfl"]
                    extra_boost = 1.0
                    if bumpkin:
                        if "Michelin Stars" in skills_dict:
                            extra_boost *= 1.05
                        if (
                            any(
                                item in cake_and_pie_items
                                for item in items.keys()
                            )
                            and "Chef Apron" in equipped_dict.values()
                        ):
                            extra_boost += 0.20
                    reward_sfl *= extra_boost
                    deliveryReward: str = f"💰 {reward_sfl:.2f} SFL"
                else:
                    # continue #Skip until release
                    reward_tickets = reward["tickets"]
                    deliveryReward = f"🎟️ {reward_tickets} tickets"
                if readytime and readytime > current_time:
                    remaining_time = readytime - current_time
                    hours_remaining = int(
                        remaining_time / (1000 * 60 * 60)
                    )  # Convert milliseconds to hours
                    minutes_remaining = int(
                        (remaining_time / (1000 * 60)) % 60
                    )  # Convert milliseconds to minutes
                    deliveryTime: str = (
                        f"{hours_remaining}hrs {minutes_remaining}mins"
                    )
                else:
                    deliveryTime = "✅ Available"

                order_status = "✅"
                if deliveryItems_value:
                    items_list: list[str] = deliveryItems_value.split(", ")
                    for item in items_list:
                        item_parts: list[str] = item.split("x", 1)
                        if len(item_parts) >= 2:
                            item_name: str = item_parts[1].strip()
                            item_quantity = int(float(item_parts[0].strip()))
                            if (
                                item_name in inventory_dict
                                and float(inventory_dict[item_name])
                                >= item_quantity
                            ):
                                continue
                            elif (
                                item_name == "sfl"
                                and balance_sfl >= item_quantity
                            ):
                                continue
                        order_status = "❌"
                        break

                ddata.append(
                    [
                        deliveryNpc,
                        f"{order_status} {deliveryItems_value}",
                        deliveryReward,
                        deliveryTime,
                    ]
                )

        columns = ["NPC", "Order and Status", "Reward", "Time"]
        df_order = pd.DataFrame(ddata, columns=columns)
        df_order.set_index("NPC", inplace=True)
        self.ft_cons["farm_delivery"].write(df_order)

        self.ft_cons["farm_delivery"].success(
            f" 📊 **Total Deliveries Completed: {deliveryTotal}**"
        )

        ti_dug: list = []
        if not isinstance(treasureIsland, dict):
            treasureIsland = {}
        if "holes" in treasureIsland:
            for i in treasureIsland["holes"]:
                dugAt: datetime = datetime.fromtimestamp(
                    int(str(treasureIsland["holes"][i]["dugAt"])[:10])
                )
                if dugAt.date() == datetime.today().date():
                    ti_dug.append(treasureIsland["holes"][i]["discovered"])

        ti_dug_today = {}
        for i in ti_dug:
            if str(i) in ti_dug_today:
                ti_dug_today[str(i)] += 1
            else:
                ti_dug_today[str(i)] = 1

        sorted_ti_dug_today = sorted(
            ti_dug_today.items(), key=lambda x: x[1], reverse=True
        )

        df_dugs = pd.DataFrame(
            sorted_ti_dug_today, columns=["Rewards Dug", "Quantity"]
        )
        df_dugs.set_index("Rewards Dug", inplace=True)

        dug_total_count: int = sum(ti_dug_today.values())

        if dug_total_count > 0:
            self.ft_cons["farm_ti"].write(df_dugs)
            self.ft_cons["farm_ti"].success(
                f"📊 **Total Dugs Today: {dug_total_count}**"
            )
        else:
            self.ft_cons["farm_ti"].error(
                f" **This farm didn't use Treasure Island today**"
            )

        self.ft_cons["basket_how"].info(
            f"\n **The NPC market sales is using the values of the in game "
            + "shops, like the seeds shop or the Treasure Island one, to "
            + "calculate the prices/cost (Includes your boost)**"
        )
        self.ft_cons["basket_how"].success(
            "\n **The balloon sales is using the lowest listed price at the "
            + "Balloon and counting the 10% Goblins fee, but it doesn't "
            + "include the listing fee**"
        )

        self.ft_cons["basket_info"].info(
            f" 🏪 **NPC Market: {total_npc_market:.2f} SFL "
            + f"(${total_npc_market_usd:.2f})**"
        )
        self.ft_cons["basket_info"].write(
            f" - 🌾 Crops sell: **{crop_sells:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write(
            f" - 🍒 Fruits sell: **{fruit_sells:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write(
            f" - 🏴‍☠️ Treasure Bountys: **{bounty_sells:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write(
            f" - ⚒️ Tools cost: **-{tool_cost:.2f} SFL (Excluded in sales)**"
        )
        self.ft_cons["basket_info"].write("\n")

        self.ft_cons["basket_info"].info(
            f" 🎈 **Balloon Sales: {total_baloon_market:.2f} SFL "
            + f"(${total_baloon_market_usd:.2f})**"
        )
        self.ft_cons["basket_info"].write(
            f" - 🥚 Eggs sell: **{egg_inv_value:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write(
            f" - 🌲 Woods sell: **{wood_inv_value:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write(
            f" - ⚪ Stones sell: **{stone_inv_value:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write(
            f" - 🟠 Irons sell: **{iron_inv_value:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write(
            f" - 🟡 Golds sell: **{gold_inv_value:.2f} SFL**"
        )
        self.ft_cons["basket_info"].write("\n")

        self.ft_cons["basket_info"].success(
            f" 🚀 **Total Sales: {total_sales:.2f} SFL "
            + f"(${total_sales_usd:.2f})**"
        )

        if fruit_patches_dict:
            for patch_id, patch_data in fruit_patches_dict.items():
                fdata: dict = patch_data.get("fruit")
                if not fdata:
                    continue
                name: str = fdata.get("name", "N/A")
                havlft: int = fdata.get("harvestsLeft", 0)
                if name not in fruit:
                    fruit[name] = [(patch_id, havlft)]
                else:
                    fruit[name].append((patch_id, havlft))

            if not fruit:
                self.ft_cons["h_fruit"].error(
                    "\n **There aren't any Fruit trees.**"
                )
            else:
                for name, trees in fruit.items():
                    total_harvests_left = 0
                    fruit_harvest_left_container: DeltaGenerator = (
                        self.tab.container()
                    )
                    for (
                        tree_id,
                        tree_data,
                    ) in fruit_patches_dict.items():
                        if (
                            tree_data.get("fruit")
                            and tree_data["fruit"].get("name") == name
                        ):
                            harvests_left = tree_data["fruit"].get(
                                "harvestsLeft"
                            )
                            total_harvests_left += harvests_left

                    with fruit_harvest_left_container:
                        self.ft_cons["h_fruit"].write("\n")
                        self.ft_cons["h_fruit"].info(
                            f"\n{self.main.fruit_emojis.get(name)} **{name} "
                            + f"Harvest Left: {total_harvests_left}**"
                        )
                        for (
                            tree_id,
                            tree_data,
                        ) in fruit_patches_dict.items():
                            if (
                                tree_data.get("fruit")
                                and tree_data["fruit"].get("name") == name
                            ):
                                harvests_left = tree_data["fruit"].get(
                                    "harvestsLeft"
                                )
                                self.ft_cons["h_fruit"].write(
                                    f" - 🌳 **{harvests_left} Harvests Left** "
                                )
        else:
            self.ft_cons["h_fruit"].error("\n **There aren't Fruit trees.**")

        total_value_wearable = 0
        bump_price_usd = 0
        level_price = 0
        if bumpkin:
            image_url: int = bump_url.rfind("v1_")
            if image_url != -1:
                # Extract the substring after "v1_"
                # fmt: off
                bump_url_last: str = bump_url[image_url + len("v1_"):]
                # fmt: on
                bump_img_url: str = (
                    f'<img src="'
                    + f'https://images.bumpkins.io/nfts/{bump_url_last}.png" '
                    + f"width = 100%>"
                )
                self.bt_cons["bump_info"].markdown(
                    bump_img_url, unsafe_allow_html=True
                )
                # Create lists to store the keys and values

            self.bt_cons["bump_general"].info(
                f" #️⃣ **Bumpkin ID: #{bump_id}**"
            )

            current_lvl = None
            for level, info in self.main.xp_dict.items():
                assert isinstance(info["Total XP"], int)
                if bump_xp >= info["Total XP"]:
                    current_lvl: int | None = level

            if current_lvl is None:
                current_lvl = max(self.main.xp_dict.keys())

            if current_lvl == max(self.main.xp_dict.keys()):
                xp_needed = 0
                nextlvl_xp = 0
                extra_xp = 0
            else:
                if current_lvl in self.main.xp_dict:
                    level_info = self.main.xp_dict[current_lvl]
                    assert isinstance(level_info["Total XP"], int)
                    if level_info["XP_next"] is not None:
                        xp_needed = level_info["XP_next"] - (
                            bump_xp - level_info["Total XP"]
                        )
                        nextlvl_xp = level_info["XP_next"]
                        extra_xp = nextlvl_xp - xp_needed
                    else:
                        xp_needed = 0
                        nextlvl_xp = 0
                        extra_xp = 0
                else:
                    xp_needed = 0
                    nextlvl_xp = 0
                    extra_xp = 0

            new_total_xp = bump_xp + total_xp

            new_lvl = None
            for level, info in self.main.xp_dict.items():
                assert isinstance(info["Total XP"], int)
                if new_total_xp >= info["Total XP"]:
                    new_lvl = level

            if new_lvl is None:
                new_lvl = max(self.main.xp_dict.keys())

            if new_lvl == max(self.main.xp_dict.keys()):
                new_xp_needed = "N/A"
                new_nextlvl_xp = "N/A"
                new_extra_xp = "N/A"
            else:
                level_info: dict[str, int | None] = self.main.xp_dict[new_lvl]
                if (
                    new_lvl in self.main.xp_dict
                    and level_info["XP_next"] is not None
                ):
                    assert isinstance(level_info["Total XP"], int)
                    new_xp_needed = level_info["XP_next"] - (
                        new_total_xp - level_info["Total XP"]
                    )
                    new_nextlvl_xp = level_info["XP_next"]
                    new_extra_xp = new_nextlvl_xp - new_xp_needed
                else:
                    new_xp_needed = "N/A"
                    new_nextlvl_xp = "N/A"
                    new_extra_xp = "N/A"
            level_price = (bump_xp / 500) * self.main.sfl_price
            # Check if the values are floats before rounding
            if isinstance(new_xp_needed, float):
                new_xp_needed = round(new_xp_needed, 1)
            if isinstance(new_nextlvl_xp, float):
                new_nextlvl_xp = round(new_nextlvl_xp, 1)
            if isinstance(new_extra_xp, float):
                new_extra_xp = round(new_extra_xp, 1)
            try:
                filtered_df = wearable_list(
                    self.main, equipped_dict, return_type="filtered_df"
                )
            except Exception as e:
                self.worth_cons["farm_worth_nft"].error(
                    "Error reading the Opensea Prices"
                )
                filtered_df = pd.DataFrame()
            try:
                total_value_wearable = wearable_list(
                    self.main, equipped_dict, return_type="total"
                )
            except Exception as e:
                self.worth_cons["farm_worth_nft"].error(
                    "Error reading the Opensea Prices"
                )
                total_value_wearable = 0
            bump_price_usd = total_value_wearable + level_price
            assert isinstance(bump_price_usd, float)

            self.bt_cons["bump_info"].write("\n")
            self.bt_cons["bump_info"].success(
                f"\n📊 Total Worth Estimate: **${bump_price_usd:.2f}**"
            )

            self.bt_cons["bump_worth_how"].error(
                f"**Note that this info in linked to the last state of the "
                + "bumpkin in that farm, if the player changed the wearables "
                + "and didn't log again in their farm the info is going to be "
                + "outdated, you can use the Bumpkin ID search to see the "
                + "current state.**"
            )
            self.bt_cons["bump_worth_how"].info(
                f"The value of **Levels Price** are calculated using "
                + "**500 XP = 1 SFL**, considering this kinda as average "
                + "value cost of the most used meals XP and lowered a little "
                + "bit to also **'value the time'**."
            )
            self.bt_cons["bump_worth_how"].success(
                f"For **Bumpkin Wearables**, it uses the **average between "
                + "the last sold price and the current lowest listing price "
                + "on Opensea**, which is updated 1-2 times per day "
                + "(semi-manually)."
            )

            self.bt_cons["bump_general"].write(
                f" - 📗 Current Level: **{current_lvl}**"
            )
            self.bt_cons["bump_general"].write(
                f" - 📘 Current Total XP: **{round(bump_xp, 1)}**"
            )
            if current_lvl == max(self.main.xp_dict.keys()):
                self.bt_cons["bump_general"].write(
                    f" - 📙 Current Progress: **(MAX)**"
                )
                self.bt_cons["bump_general"].write(
                    f" - ⏭️ XP for Next LVL: **(MAX)**"
                )
            else:
                self.bt_cons["bump_general"].write(
                    f" - 📙 Current Progress: **["
                    + f"{round(extra_xp, 1)} / {nextlvl_xp}]**"
                )
                self.bt_cons["bump_general"].write(
                    f" - ⏭️ XP for Next LVL: **{round(xp_needed, 1)}**"
                )
            self.bt_cons["bump_general"].write("\n")
            self.bt_cons["bump_general"].success(
                f"\n📊 Levels Price Estimate: **${level_price:.2f}**"
            )

            total_quantity: int = sum(food_quantity.values())
            self.bt_cons["bump_general"].write(
                f" - 🍲 Quantity of Meals: **{total_quantity}**"
            )
            self.bt_cons["bump_general"].write(
                f"\n - 🔼 Total XP from Meals: **{total_xp:.2f}**"
            )

            self.bt_cons["bump_general"].write("\n")
            if new_lvl == max(self.main.xp_dict.keys()):
                self.bt_cons["bump_general"].info(
                    f" 📚 Level after Eating: **{new_lvl} (MAX)**"
                )
            else:
                self.bt_cons["bump_general"].info(
                    f" 📚 Level after Eating: **{new_lvl} - "
                    + f"[{new_extra_xp} / {new_nextlvl_xp}]**"
                )
            self.bt_cons["bump_general"].success(
                f" 📊 New Total XP: **{new_total_xp:.1f}**"
            )

            self.bt_cons["bump_wearables"].write(filtered_df)
            self.bt_cons["bump_wearables"].success(
                f"\n📊 Wearables Total Price: **${total_value_wearable:.2f}**"
            )

            # Create lists to store the keys and descriptions
            skill_names = []
            skill_descriptions = []

            # Iterate over the dictionary and extract the keys and descriptions
            for key in skills_dict:
                skill_names.append(key)
                skill_descriptions.append(
                    self.main.skills_description.get(
                        key, "Description not available"
                    )
                )
            # Create a DataFrame
            df_skills = pd.DataFrame(
                {
                    "Skill": skill_names,
                    "Description": skill_descriptions,
                }
            )
            df_skills.set_index("Skill", inplace=True)

            # Write the DataFrame
            self.bt_cons["bum_skill"].write(df_skills)
            bump_achi_total: int = len(bump_achi)
            self.bt_cons["bum_skill"].success(
                f"\n🏅 Total Achivements: **{bump_achi_total}**"
            )

            gathe_activity_values = (
                [("Trees Chopped", trees_chopped)]
                + [
                    (activity, value)
                    for activity, value in mined_activities.items()
                ]
                + [("Eggs", egg_collected)]
                + [("SFL Earn", sfl_earn)]
                + [("SFL Spent", sfl_spent)]
            )
            df_gather = pd.DataFrame(
                gathe_activity_values, columns=["Activity", "Value"]
            )
            df_gather["Value"] = df_gather["Value"].round(1)
            df_gather.set_index("Activity", inplace=True)
            self.bt_cons["gather"].write(df_gather)

            self.bt_cons["harvest"].info(
                f"🌾 **Total Crops Harvested: {harvested_total}**"
            )
            self.bt_cons["harvest"].success(
                f"🍒 **Total Fruits Harvested: {fruit_total}**"
            )
            harvest_activity_values = [
                (activity, value)
                for activity, value in harvested_activities.items()
            ]
            harvest_sorted_activity_values = sorted(
                harvest_activity_values,
                key=lambda x: x[1],
                reverse=True,
            )
            harvest_df_activities = pd.DataFrame(
                harvest_sorted_activity_values,
                columns=["Activity", "Value"],
            )
            harvest_df_activities.set_index("Activity", inplace=True)
            self.bt_cons["harvest"].write(harvest_df_activities)

            self.bt_cons["dug"].info(
                f"🔵 **Total Sand Shovel Used: {sandshovel}**"
            )
            self.bt_cons["dug"].info(f"🟤 **Total Sand Drill Used: {drill}**")
            if sandshovel is not None and drill is not None:
                self.bt_cons["dug"].success(
                    f"📊 **Total Holes Dug: {dug_holes}**"
                )
            dug_activity_values = [
                (activity, value) for activity, value in dug_activities.items()
            ]
            dug_sorted_activity_values = sorted(
                dug_activity_values,
                key=lambda x: x[1],
                reverse=True,
            )
            dug_df_activities = pd.DataFrame(
                dug_sorted_activity_values,
                columns=["Activity", "Value"],
            )
            dug_df_activities.set_index("Activity", inplace=True)
            self.bt_cons["dug"].write(dug_df_activities)

            self.bt_cons["bum_cook"].info(
                f"🍳 **Total Meals Cooked: {cooked_total}**"
            )
            cook_activity_values = [
                (activity, value)
                for activity, value in cooked_activities.items()
            ]
            cook_sorted_activity_values = sorted(
                cook_activity_values,
                key=lambda x: x[1],
                reverse=True,
            )
            cook_df_activities = pd.DataFrame(
                cook_sorted_activity_values,
                columns=["Activity", "Value"],
            )
            cook_df_activities.set_index("Activity", inplace=True)
            self.bt_cons["bum_cook"].write(cook_df_activities)

            self.bt_cons["food"].info(f"🤤 **Total Meals Fed: {fed_total}**")
            activity_values = [
                (activity, value) for activity, value in fed_activities.items()
            ]
            sorted_activity_values = sorted(
                activity_values, key=lambda x: x[1], reverse=True
            )
            df_activities = pd.DataFrame(
                sorted_activity_values,
                columns=["Activity", "Value"],
            )
            df_activities.set_index("Activity", inplace=True)
            self.bt_cons["food"].write(df_activities)
        else:
            self.bt_cons["status_bumpkin"].error(
                f" **There aren't Bumpkins in this Farm.**"
            )

        expansion_resources: list[str] = ["Wood", "Stone", "Iron", "Gold"]
        previous_resources = {}

        expansion_num = 0
        for expansion, res in expansions.items():
            if not res:
                expansion_num = int(expansion.split("_")[1].rstrip("ABCDEF"))
                self.worth_cons["farm_worth_exp"].info(
                    f"🔼 **This Farm is in the Expansion {expansion_num}**"
                )
                continue  # move on to the next expansion

            for key, value in total_resources.items():
                if key not in res or value > res[key]:
                    break
            else:
                expansion_num = int(expansion.split("_")[1].rstrip("ABCDEF"))
                self.worth_cons["farm_worth_exp"].info(
                    f"🔼 **This Farm is in the Expansion {expansion_num}**"
                )
                break

        total_price_exp = Decimal(0)
        expansion_price_usd = Decimal(0)
        current_resources = {}
        for i in range(3, expansion_num + 1):
            expansion_key: str = f"expansion_{i}"
            res_cost: dict = expansions_cost[expansion_key]
            current_resources: dict = {}
            for resource in expansion_resources:
                current_resources[resource] = res_cost.get(
                    resource, 0
                ) + previous_resources.get(resource, 0)
            previous_resources: dict = current_resources
            expansion_price: Decimal = get_expansion_price(current_resources)
            expansion_price_usd: Decimal = Decimal(expansion_price) * Decimal(
                self.main.sfl_price
            )
            total_price_exp += expansion_price_usd

        total_price = 0
        total_price_usd = 0

        for building in building_items:
            if "Hen House" in building:
                if "Hen House" in buildings_dict:
                    building_count = sum(
                        1
                        for b in buildings_dict["Hen House"]
                        if "createdAt" in b
                    )
                    if building_count > 1:
                        buildings_dict["Hen House2"] = buildings_dict[
                            "Hen House"
                        ][-1:]
                        buildings_dict["Hen House"] = buildings_dict[
                            "Hen House"
                        ][:-1]
                        building_items.append("Hen House2")
            else:
                continue

        data_buildings: list = []

        if not any(building in buildings_dict for building in building_items):
            self.worth_cons["farm_worth_bui"].error("There aren't buildings")
        else:
            for building in building_items:
                if building in buildings_dict:
                    if buildings_dict[building]:
                        building_count: int = sum(
                            1
                            for b in buildings_dict[building]
                            if "createdAt" in b
                        )
                    else:
                        building_count = 1
                    building_price: Decimal = get_building_price(building)
                    if (
                        building == "Hen House2"
                        and "Hen House2" in buildings_farm
                    ):
                        continue
                    buildings_farm[building] = buildings_dict[building]
                    buildings_farm_price[building] = building_price
                    total_building_price: Decimal = building_price * Decimal(
                        building_count
                    )
                    total_building_price_usd: Decimal = Decimal(
                        total_building_price
                    ) * Decimal(self.main.sfl_price)
                    data_buildings.append(
                        [
                            building_count,
                            building,
                            total_building_price_usd,
                        ]
                    )
                    total_price += total_building_price
                    total_price_usd += total_building_price_usd
                else:
                    continue

            if data_buildings:
                df_buildings = pd.DataFrame(
                    data_buildings,
                    columns=["Quantity", "Building", "Cost Price"],
                )
                df_buildings.set_index("Quantity", inplace=True)
                df_buildings["Cost Price"] = pd.to_numeric(
                    df_buildings["Cost Price"], errors="coerce"
                )
                df_buildings.sort_values(
                    by="Cost Price", ascending=False, inplace=True
                )
                df_buildings["Cost Price"] = "$" + df_buildings[
                    "Cost Price"
                ].apply(lambda x: f"{x:.2f}")
                self.worth_cons["farm_worth_bui"].write(df_buildings)
            else:
                self.worth_cons["farm_worth_bui"].write("No buildings found.")
            self.worth_cons["farm_worth_bui"].success(
                f"📊 Total Cost Price: **${total_price_usd:.2f}**"
            )

        farm_nft: list[float | DataFrame] = [
            nft_buffs(self.main, inventory_dict, return_type="total")
        ]
        total_farm_nft: float | DataFrame | int = sum(farm_nft)
        total_farm_nft_usd = Decimal(str(total_farm_nft))

        # farm_worth_nft.info(" **This includes tradable NFT's that are
        # currently withdrawables**")
        self.worth_cons["farm_worth_nft"].write(
            nft_buffs(self.main, inventory_dict, return_type="result_df")
        )
        self.worth_cons["farm_worth_nft"].success(
            f"\n📊 Total Price: **$"
            + f"{nft_buffs(self.main, inventory_dict, return_type='total'):.2f}"
            + "**"
        )
        # farm_worth_decorative.info(" **This includes Flags (fixed $5),
        # NFT's from Helios and also others non withdrawables**")

        flag_items = {
            item: quantity
            for item, quantity in inventory_dict.items()
            if item.endswith("Flag")
        }
        nontradable_list: list = []

        flag_items = {
            item: quantity
            for item, quantity in inventory_dict.items()
            if item.endswith("Flag")
        }
        for item, quantity in flag_items.items():
            price = 5.00 * int(quantity)
            nontradable_list.append(
                {"item": item, "quantity": quantity, "price": price}
            )

        for item, quantity in inventory_dict.items():
            if item in helios_sfl:
                price = (helios_sfl[item] * int(quantity)) * (
                    self.main.sfl_price
                )
                nontradable_list.append(
                    {
                        "item": item,
                        "quantity": quantity,
                        "price": price,
                    }
                )

        for item, quantity in inventory_dict.items():
            if item in nft_resources:
                resources_nft: dict[str, float | int] = nft_resources[item]
                price_nft = Decimal(0)
                for (
                    resource,
                    resource_quantity,
                ) in resources_nft.items():
                    if resource == "SFL":
                        price_nft += Decimal(resource_quantity)
                    elif resource in resources_items:
                        if resource == "Wood":
                            price_nft += Decimal(resource_quantity) * Decimal(
                                wood_price_converted
                            )
                        elif resource == "Stone":
                            price_nft += Decimal(resource_quantity) * Decimal(
                                stone_price_converted
                            )
                        elif resource == "Iron":
                            price_nft += Decimal(resource_quantity) * Decimal(
                                iron_price_converted
                            )
                        elif resource == "Gold":
                            price_nft += Decimal(resource_quantity) * Decimal(
                                gold_price_converted
                            )
                temp_price: Decimal = (
                    price_nft * Decimal(quantity) * Decimal(self.main.sfl_price)
                )
                nontradable_list.append(
                    {
                        "item": item,
                        "quantity": quantity,
                        "price": temp_price,
                    }
                )

        nontradable_dict: list = []

        for item in nontradable_list:
            price: float = round(float(item["price"]), 2)
            nontradable_dict.append(
                {
                    "item": item["item"],
                    "quantity": item["quantity"],
                    "price": price,
                }
            )

        nontradable_df: pd.DataFrame = pd.DataFrame(
            nontradable_dict, columns=["item", "quantity", "price"]
        )
        nontradable_df = nontradable_df.rename(
            columns={
                "item": "NFT",
                "quantity": "Quantity",
                "price": "Total Price",
            }
        )
        nontradable_df = nontradable_df.sort_values(
            by="Total Price", ascending=False
        )
        nontradable_df = nontradable_df.reset_index(drop=True)
        nontradable_df = nontradable_df.set_index("NFT")
        nontradable_df["Total Price"] = nontradable_df["Total Price"].apply(
            lambda x: f"${x:.2f}"
        )
        total_price_sum: float = (
            nontradable_df["Total Price"]
            .str.replace("$", "", regex=False)
            .astype(float)
            .sum()
        )

        self.worth_cons["farm_worth_decorative"].write(nontradable_df)
        self.worth_cons["farm_worth_decorative"].success(
            f"\n📊 Total Price: **${total_price_sum:.2f}**"
        )

        # Create a dictionary of Average Price before removing the column
        try:
            data_nft: DataFrame | None = nft_price(self.main)
        except Exception as e:
            self.worth_cons["farm_worth_nft"].error(
                f"Error reading the Opensea Prices {e}"
            )
            data_nft = None
        if data_nft is None:
            data_nft = pd.DataFrame()
        avg_price_dict: list[dict[Hashable, Any]] = data_nft.to_dict("records")
        for i, dictionary in enumerate(avg_price_dict):
            avg_price_dict[i] = {k: v for k, v in dictionary.items()}

        legacy_skill: dict[str, float] = {
            "Liquidity Provider": 150.0,
            "Artist": [
                item
                for item in avg_price_dict
                if item["NFT"] == "Apprentice Beaver"
            ][0]["Average Price"],
            "Coder": [
                item for item in avg_price_dict if item["NFT"] == "Scarecrow"
            ][0]["Average Price"]
            * 3,
            "Discord Mod": [
                item
                for item in avg_price_dict
                if item["NFT"] == "Apprentice Beaver"
            ][0]["Average Price"],
            "Logger": [
                item
                for item in avg_price_dict
                if item["NFT"] == "Apprentice Beaver"
            ][0]["Average Price"]
            * 2,
            "Lumberjack": [
                item
                for item in avg_price_dict
                if item["NFT"] == "Woody the Beaver"
            ][0]["Average Price"]
            * 2,
            "Gold Rush": [
                item for item in avg_price_dict if item["NFT"] == "Nugget"
            ][0]["Average Price"]
            * 3,
            "Prospector": [
                item for item in avg_price_dict if item["NFT"] == "Tunnel Mole"
            ][0]["Average Price"]
            * 10,
            "Wrangler": [
                item
                for item in avg_price_dict
                if item["NFT"] == "Speed Chicken"
            ][0]["Average Price"],
            "Barn Manager": [
                item for item in avg_price_dict if item["NFT"] == "Rich Chicken"
            ][0]["Average Price"],
            "Seed Specialist": [
                item
                for item in avg_price_dict
                if item["NFT"] == "Lunar Calendar"
            ][0]["Average Price"],
            "Green Thumb": 1.0,
        }

        rows: list = []

        for item in inventory_dict.keys():
            if item in legacy_skill:
                skill_farm: float = legacy_skill[item]
                nft = item
                price = skill_farm

                if isinstance(skill_farm, list):
                    nft = skill_farm[0]["NFT"]
                    if len(skill_farm) == 2:
                        price = skill_farm[0]["Average Price"] * skill_farm[1]
                    else:
                        price = skill_farm[0]["Average Price"]

                rows.append([item, price])

        if not rows:
            self.worth_cons["farm_worth_skill"].error(
                "This Farm doesn't have Legacy Skills"
            )
            skill_farm_total_usd = 0
        else:
            df_legacy_skills = pd.DataFrame(
                rows, columns=["Skill", "Price Estimate"]
            )
            skill_farm_total_usd = Decimal(
                df_legacy_skills["Price Estimate"].sum()
            )
            df_legacy_skills["Price Estimate"] = pd.to_numeric(
                df_legacy_skills["Price Estimate"], errors="coerce"
            )
            df_legacy_skills.sort_values(
                by="Price Estimate", ascending=False, inplace=True
            )
            df_legacy_skills["Price Estimate"] = "$" + df_legacy_skills[
                "Price Estimate"
            ].apply(lambda x: f"{x:.2f}")
            df_legacy_skills.set_index("Skill", inplace=True)
            self.worth_cons["farm_worth_skill"].write(df_legacy_skills)
            self.worth_cons["farm_worth_skill"].success(
                f"📊 Total Estimate Value: **{skill_farm_total_usd:.2f}**"
            )

        if bumpkin:
            self.worth_cons["farm_worth_bump"].info(
                f" #️⃣ **Bumpkin ID: #{bump_id}**"
            )
            self.worth_cons["farm_worth_bump"].write(
                f"\n - 👖 Wearables Total Price: **${total_value_wearable:.2f}**"
                + f" \n - 📚 Levels Price Estimate: **${level_price:.2f}**"
            )
            self.worth_cons["farm_worth_bump"].write(f"\n")
            self.worth_cons["farm_worth_bump"].success(
                f"\n 📊 Bumpkin Worth Estimate: **${bump_price_usd:.2f}**"
            )
        else:
            pass

        bbucks = expansion_num - 3
        bbucks_usd = bbucks * 0.1
        expansion_price_usd_bbucks: Decimal = Decimal(
            str(expansion_price_usd)
        ) + Decimal(str(bbucks_usd))
        total_price_sum_usd = Decimal(total_price_sum)
        balance_sfl_usd: Decimal = Decimal(balance_sfl) * Decimal(
            self.main.sfl_price
        )
        farm_inv_sfl: Decimal = Decimal(balance_sfl_usd) + Decimal(
            total_sales_usd
        )

        total_farm_usd: Decimal = (
            total_price_usd
            + expansion_price_usd_bbucks
            + total_sales_usd
            + total_farm_nft_usd
            + total_price_sum_usd
            + skill_farm_total_usd
            + balance_sfl_usd
        )

        self.worth_cons["farm_worth"].info(
            f"💰 Farm Inventory and SFL: **${farm_inv_sfl:.2f}**"
        )
        self.worth_cons["farm_worth"].success(
            f"🏡 **Farm Worth Estimate: ${total_farm_usd:.2f}**"
        )
        if bumpkin:
            total_farm_bump_usd: Decimal = Decimal(total_farm_usd) + Decimal(
                bump_price_usd
            )
            self.worth_cons["farm_worth"].warning(
                f"📊 **Estimate with Bumpkin: ${total_farm_bump_usd:.2f}**"
            )
        else:
            pass

        output: str = ""
        for resource, quantity in current_resources.items():
            output += f"{resource} {quantity}, "
        output = output[:-2]
        self.worth_cons["farm_worth_exp"].write(
            f" - 📋 **Resources used:** {output} and {bbucks} Block Bucks"
        )

        self.worth_cons["farm_worth_exp"].write("\n")
        self.worth_cons["farm_worth_exp"].success(
            f"📊 Total Cost Price: **${expansion_price_usd_bbucks:.2f}**"
        )

        self.worth_cons["farm_worth_how"].info(
            f"The value of **Buildings, Expansions and Extras** are calculated "
            + "using the **lowest listed price** for the required resources "
            + "**at the Balloon**."
        )
        self.worth_cons["farm_worth_how"].success(
            f"For **Tradables NFTs**, it uses the **average between the "
            + "last sold price and the current lowest listing price on "
            + "Opensea**, which is updated 1-2 times per day (semi-manually). "
            + "And the **Extras** includes Flags (fixed $5), NFT's from "
            + "Helios and also others non withdrawables"
        )
        self.worth_cons["farm_worth_how"].info(
            f"The **Legacy Skills** are calculated **pairing them with "
            + "NFT's that have similar boost** and also considering their "
            + "supply. Examples, **Seed Specialist = Lunar Calendar** or "
            + "**Gold Rush = Nugget x 3**."
        )
        # except Exception as e:
        #     error_message = f"Error occurred in Farm {self.farm_id}: {str(e)}"
        #     sys.stderr.write(error_message)
        #     # Display the error message in Streamlit
        #     st.error(error_message)

    def create_farm_tab(self, tab: DeltaGenerator) -> dict[str, DeltaGenerator]:
        left_col: DeltaGenerator
        middle_col: DeltaGenerator
        right_col: DeltaGenerator
        left_col, middle_col, right_col = tab.columns([3, 3, 3], gap="medium")
        containers: dict[str, DeltaGenerator] = {}
        with left_col:
            containers["hoarder"] = st.expander(
                "\U0001F69C **HOARDER LIMITS**", expanded=True
            )
            containers["spend"] = st.expander(
                "🤑 **SPENT CHECKER**", expanded=True
            )
            containers["dawn_breaker"] = st.expander(
                "🌄 **Dawn Breaker**", expanded=False
            )
        with middle_col:
            containers["farm_info"] = st.expander(
                "🏝️ **FARM RESOURCES**", expanded=True
            )
            containers["farm_delivery"] = st.expander(
                "🚚 **DELIVERIES**", expanded=True
            )
            containers["c_mutant"] = st.expander(
                "\U0001F414 **MUTANT CHICKENS DROP**", expanded=True
            )
            containers["h_fruit"] = st.expander(
                "\U0001f352 **FRUIT HARVEST LEFT**", expanded=True
            )
        with right_col:
            containers["wanderleaf"] = st.expander(
                "🧙 **WANDERLEAF**", expanded=True
            )
            containers["farm_ti"] = st.expander(
                "☠️ **TREASURE ISLAND**", expanded=True
            )
            containers["balance_check"] = st.expander(
                "💰 **SFL BALANCE**", expanded=True
            )
            containers["basket_how"] = st.expander(
                "📝 **HOW IT WORKS?**", expanded=False
            )
            containers["basket_info"] = st.expander(
                "👜  **INVENTORY CHECKER**", expanded=True
            )
        return containers

    def create_bp_tab(self, tab: DeltaGenerator) -> dict[str, DeltaGenerator]:
        containers: dict[str, DeltaGenerator] = {}
        containers["status_bumpkin"] = st.container()
        col14: DeltaGenerator
        col15: DeltaGenerator
        col16: DeltaGenerator
        col17: DeltaGenerator
        col14, col15, col16, col17 = tab.columns([2, 2, 2, 2], gap="medium")
        containers["bump_info"] = col14.expander("🖼️ PICTURE", expanded=True)
        containers["bump_worth_how"] = col14.expander(
            "📝 **HOW IT WORKS?**", expanded=False
        )
        containers["bump_general"] = col15.expander(
            "📖 **GENERAL**", expanded=True
        )
        containers["bump_wearables"] = col16.expander(
            "👖 **WEARABLES**", expanded=True
        )
        containers["bum_skill"] = col17.expander(
            "🏹 **SKILLS & ACHIEVEMENTS**", expanded=True
        )

        tab.divider()

        col4: DeltaGenerator
        col5: DeltaGenerator
        col6: DeltaGenerator
        col7: DeltaGenerator
        col4, col5, col6, col7 = tab.columns([2, 2, 2, 2], gap="medium")
        containers["gather"] = col4.expander("⚒️ **RESOURCES**", expanded=True)
        containers["harvest"] = col4.expander(
            "🌱 **CROPS/FRUITS**", expanded=True
        )
        containers["dug"] = col5.expander(
            "🏴‍☠️ **TREASURE ISLAND**", expanded=True
        )
        containers["bum_cook"] = col6.expander(
            "👨‍🍳 **MEALS COOKED**", expanded=True
        )
        containers["food"] = col7.expander("🍲 **MEALS FED**", expanded=True)
        return containers

    def create_worth_tab(
        self, tab: DeltaGenerator
    ) -> dict[str, DeltaGenerator]:
        containers: dict[str, DeltaGenerator] = {}
        col8: DeltaGenerator
        col9: DeltaGenerator
        col10: DeltaGenerator
        col11: DeltaGenerator
        col8, col9, col10, col11 = tab.columns([2, 2, 2, 2], gap="medium")
        containers["farm_worth_how"] = col8.expander(
            "📝 **HOW IT WORKS?**", expanded=False
        )
        containers["farm_worth"] = col8.expander(
            "💎 **TOTAL WORTH ESTIMATE**", expanded=True
        )
        containers["farm_worth_skill"] = col8.expander(
            "🗝️ **LEGACY SKILL**", expanded=True
        )
        containers["farm_worth_nft"] = col9.expander(
            "💸 **TRADABLES NFT'S**", expanded=True
        )
        containers["farm_worth_exp"] = col10.expander(
            "🏝️ **EXPANSIONS**", expanded=True
        )
        containers["farm_worth_bui"] = col10.expander(
            "🏗️ **BUILDINGS**", expanded=True
        )
        containers["farm_worth_bump"] = col11.expander(
            "👨‍🌾 **BUMPKIN WORTH ESTIMATE**", expanded=True
        )
        containers["farm_worth_decorative"] = col11.expander(
            "🗿 **EXTRAS**", expanded=True
        )
        return containers

    def get_containers(self) -> dict[str, DeltaGenerator]:
        return self.ft_cons
