import discord
from og import *

with open("config.json") as config:
    data = json.load(config)
    token = data["token"]
client = discord.Client()


def build_embed(lat, lon):
    target_list = get_targets(lat, lon)
    limiter = 20
    if len(target_list) >= limiter:
        target_list = target_list[:limiter]
    embed = discord.Embed(
        title="JDAM Coordinate Finder.",
        description=str(len(target_list)) + " targets shown.",
        colour=discord.Colour.blue()
    )

    for bogey in target_list:
        embed.add_field(name=bogey.Type,
                        value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                            round(bogey.Elev)) + "ft\nDist:   " + str(round(bogey.Dist, 4)) + "\n",
                        inline=True)
    return embed


def check_valid(message):
    try:
        msg = message.content
        grouped = msg.split(" ")
        if len(grouped[0]) == 6 and len(grouped[1]) == 6:
            return True
        else:
            return False
    except:
        return False


@client.event
async def on_ready():
    print("Logged in as " + client.user.name)
    return


@client.event
async def on_message(message):
    print(message.author.name + ": " + message.content)
    if message.author == client.user:
        return

    elif check_valid(message):
        grouped = message.content.split(" ")
        print("Detected Lat: " + str(grouped[0]))
        print("Detected Lon: " + str(grouped[1]))
        await client.send_message(message.channel, "Those are valid coordinates. Fetching....")
        await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1]))


client.run(token, bot=False)
