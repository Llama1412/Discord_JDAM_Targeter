import discord
from og import *

with open("config.json") as config:
    data = json.load(config)
    token = data["token"]
client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as " + client.user.name)
    print(get_targets("431503", "401909"))
    return


@client.event
async def on_message(message):
    print(message.author.name + ": " + message.content)
    if message.author.name == client.user:
        return
    elif message.content.startswith("?hi"):
        await client.send_message(message.channel, "Hello!")


client.run(token, bot=False)
