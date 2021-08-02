#!/usr/bin/env python3
"""Script to send an embed to a discord channel with CTFTime scores"""

import datetime
import os

import pymongo
import pytz
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.anjon.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
mydb = client["testdbname"]
collection = mydb["testcollectionname"]


TEAM_ID = "137561"

HEADERS = {"User-Agent": "Cluster0"}

PFP_URL = "https://cdn.discordapp.com/attachments/719605546101113012/731453497479790672/ctftime.png"


def scrape_website(team_id):
    """Downloads the website and scapes the rating"""
    page = requests.get(f"https://ctftime.org/team/{team_id}", headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")
    print(soup)
    rating_div = soup.find(id="rating_2021")
    rating_a = str(rating_div.select('a[href="/stats/NO"]')[0])
    rating_a = rating_a.replace('<a href="/stats/NO">', "").replace("</a>", "")
    return int(rating_a)


def get_world_rating(team_id):
    """Parses the JSON and gets the data"""
    response = requests.get(
        f"https://ctftime.org/api/v1/teams/{team_id}/", headers=HEADERS)
    print(response)
    return int(response.json()["rating"][0]["2021"]["rating_place"])


def post_discord_message(webhook,data):
    """Posts to the discord webhook url"""
    requests.post(webhook, json=data)


def main():
    
    parser = argparse.ArgumentParser()

    webhooks_group = parser.add_mutually_exclusive_group(required=True)
    webhooks_group.add_argument('-w', '--webhooks', metavar='url', nargs='+',
                                help='a discord webhook which the data will be send to')
    args = parser.parse_args()
    
    """The main function that will be ran when the script runs"""
    last_entry = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    try:
        last_rating = {
            "world": int(last_entry["world"])
        }
    except TypeError:
        last_rating = {
            "world": "NO_DATA"
        }

    position = get_world_rating(TEAM_ID)

    is_changed = 1

    if last_rating["world"] == "NO_DATA":
        # Hvis vi mangler data
        change = ":arrow_right:"
        last_rating['world'] = position
    else:
        if position > last_rating["world"]:
            # Vi har falt
            change = ":arrow_down:"
        elif position < last_rating["world"]:
            # Vi har gått opp
            change = ":arrow_up:"
        else:
            is_changed = 0
            # Ingen endring
            change = ":arrow_right:"


    time_now = pytz.timezone(
        "Europe/Oslo").localize(datetime.datetime.now().replace(microsecond=0)).isoformat()

    try:
        if last_entry["checked_at"] is None:
            last_checked = time_now
        else:
            last_checked = last_entry["checked_at"]
    except TypeError:
        last_checked = time_now
    if is_changed == 1:
        collection.insert_one(
            {"checked_at": time_now, "world": position})


        post_discord_message(args.webhooks,{
            "username": "CTFTime",
            "avatar_url": PFP_URL,
            "embeds": [{

                "title": "CTFTime ranking update",
                "description": f"World: {change} {position}\n",
                "color": 11610890,
                "fields": [ {
                    "name": "Last rating",
                    "value": f"World: {last_rating['world']}\n",
                    "inline": True
                }]
            }]
        })



if __name__ == "__main__":
    main()
