import discord
from og import *

with open("config.json") as config:
    data = json.load(config)
    token = data["token"]
client = discord.Client()


# def print_table(target_list):


@client.event
async def on_ready():
    print("Logged in as " + client.user.name)
    # print(get_targets("431503", "401909"))
    return


@client.event
async def on_message(message):
    print(message.author.name + ": " + message.content)
    if message.author.name == client.user:
        return
    elif message.content.startswith("?hi"):
        await client.send_message(message.channel, "Hello!")
        target_list = get_targets("431503", "401909")

        embed = discord.Embed(
            title="JDAM Coordinate Finder",
            colour=discord.Colour.blue()
        )

        for bogey in target_list[:5]:
            embed.add_field(name=bogey.Type,
                            value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(round(bogey.Elev)) + "ft\nDist:   " + str(round(bogey.Dist,4)),
                            inline=True)

        await client.send_message(message.channel, embed=embed)


client.run(token, bot=False)
