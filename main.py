import discord
import json

with open("config.json") as config:
    data = json.load(config)
    token = data["token"]

