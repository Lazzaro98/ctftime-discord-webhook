#!/usr/bin/python3

import os

import requests
from dotenv import load_dotenv

load_dotenv()

CTFTIME_URL = "https://ctftime.org/api/v1/teams/113107/"
HEADERS = {"User-Agent": "Corax"}

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def get_rating_place():
    """Parses the JSON and gets the data"""
    response = requests.get(CTFTIME_URL, headers=HEADERS)
    return response.json()["rating"][0]["2020"]["rating_place"]


def post_discord_message(data):
    """Posts to the discord webhook url"""
    requests.post(DISCORD_WEBHOOK_URL, json=data)


position = get_rating_place()

print(f"World position: {position}")

change = ":arrow_right:"

position_norway = "Who knows?"
change_norway = ":arrow_right:"

post_discord_message({
    "username": f"CTFTime",
    "embeds": [{
        "title": "CTFTime ranking update",
        "description": f"World: {change} {position}\nNorway: {change_norway} {position_norway}",
        "fields": [{
            "name": "Last checked",
            "value": "Save this to a database or something",
            "inline": "True"
        }, {
            "name": "Last rating",
            "value": "Save this to a database or something",
            "inline": "True"
        }]
    }]
})
