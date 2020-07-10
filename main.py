#!/usr/bin/python3

import os

import re
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

CTFTIME_API_URL = "https://ctftime.org/api/v1/teams/113107/"
CTFTIME_URL = "https://ctftime.org/team/113107"

HEADERS = {"User-Agent": "Corax"}

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def scrape_website():
    """Downloads the website and scapes the rating"""
    page = requests.get(CTFTIME_URL, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    rating_div = soup.find(id="rating_2020")
    rating_a = str(rating_div.select('a[href="/stats/NO"]')[0])
    rating_a = rating_a.replace('<a href="/stats/NO">', "").replace("</a>", "")
    return rating_a


def get_rating_place():
    """Parses the JSON and gets the data"""
    response = requests.get(CTFTIME_API_URL, headers=HEADERS)
    return response.json()["rating"][0]["2020"]["rating_place"]


def post_discord_message(data):
    """Posts to the discord webhook url"""
    requests.post(DISCORD_WEBHOOK_URL, json=data)


position = get_rating_place()
change = ":arrow_right:"

position_norway = scrape_website()
change_norway = ":arrow_right:"


last_rating = {
    "world": "get from database",
    "norway": "get from database"
}

post_discord_message({
    "username": f"CTFTime",
    "embeds": [{
        "title": "CTFTime ranking update",
        "description": f"World: {change} {position}\nNorway: {change_norway} {position_norway}",
        "fields": [{
            "name": "Last checked",
            "value": f"Save this to a database or something",
            "inline": "True"
        }, {
            "name": "Last rating",
            "value": f"World: {last_rating['world']}\nNorway: {last_rating['norway']}",
            "inline": "True"
        }]
    }]
})
