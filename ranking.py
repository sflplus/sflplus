from typing import TYPE_CHECKING, Any
import streamlit as st
import requests
import json

if TYPE_CHECKING:
    from requests import Response


@st.cache_resource(
    ttl=7200, show_spinner="Updating Top10 ID"
)  # cache for 2 hour
def fetch_top_ten_ids():
    try:
        # Sending the request to the second API
        response: dict = requests.get(
            "https://api.sunflower-land.com/leaderboard/lanterns/1"
        ).json()
        top_ten_ids: list[Any] = [entry["id"] for entry in response["topTen"]]
        return top_ten_ids
    except Exception as e:
        print(f"Failed to fetch top ten IDs. Error: {e}")
        return []


@st.cache_resource(
    ttl=780, show_spinner="Updating Top10 lanterns"
)  # cache for 13 min
def retrieve_lanterns_data(top_ten_ids):
    # Building payload using the provided IDs
    payload = json.dumps({"ids": top_ten_ids})
    headers = {"Content-Type": "application/json"}

    # Sending the request to the first API
    response = requests.post(
        "https://api.sunflower-land.com/community/getFarms",
        headers=headers,
        data=payload,
    ).json()

    # Processing the response from the first API
    skipped_farms = response["skipped"]
    farms = response["farms"]

    lanterns_data = {}
    for farm_id, farm in farms.items():
        try:
            farm_data = farm.get("dawnBreaker", {}).get(
                "lanternsCraftedByWeek", {}
            )
            week_data = {
                str(week): farm_data.get(str(week), 0) for week in range(1, 9)
            }
            lanterns_data[str(farm_id)] = week_data
        except Exception as e:
            pass

    return lanterns_data
