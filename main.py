import discord
from og import *

with open("config.json") as config:
    data = json.load(config)
    token = data["token"]
client = discord.Client()


def build_embed(lat, lon, threat):
    target_list = get_targets(lat, lon, threat)
    embed = False
    limiter = 12
    if len(target_list) >= limiter:
        target_list = target_list[:limiter]

    if threat == 1 and len(target_list) > 0:
        embed = discord.Embed(
            title="High Threat Targets",
            description=str(len(target_list)) + "/12 targets shown.",
            colour=discord.Colour.red()
        )
    if threat == 2 and len(target_list) > 0:
        embed = discord.Embed(
            title="Medium Threat Targets",
            description=str(len(target_list)) + "/12 targets shown.",
            colour=discord.Colour.orange()
        )
    if threat == 3 and len(target_list) > 0:
        embed = discord.Embed(
            title="Low Threat Targets",
            description=str(len(target_list)) + "/12 targets shown.",
            colour=discord.Colour.green()
        )
    if threat == 4 and len(target_list) > 0:
        embed = discord.Embed(
            title="Zero Threat Targets",
            description=str(len(target_list)) + "/12 targets shown.",
            colour=discord.Colour.blue()
        )
    if threat == 5 and len(target_list) > 0:
        embed = discord.Embed(
            title="Static Targets",
            description=str(len(target_list)) + "/12 targets shown.",
            colour=discord.Colour.teal()
        )
    if threat == 6 and len(target_list) > 0:
        embed = discord.Embed(
            title="Unknown Targets",
            description="Please inform Llama of any targets in here.",
            colour=discord.Colour.default()
        )

    if embed is not False:
        for bogey in target_list:
            embed.add_field(name=bogey.Type,
                            value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                round(bogey.Elev)) + "ft\nDist:   " + str(round(bogey.Dist, 4)) + "\n",
                            inline=True)
        return embed

    else:
        return False


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
    if message.author is not client:
        print(message.author.name + ": " + message.content)
    if message.author == client.user:
        return

    elif check_valid(message):
        grouped = message.content.split(" ")
        print("Detected Lat: " + str(grouped[0]))
        print("Detected Lon: " + str(grouped[1]))
        await client.send_message(message.channel, "Those are valid coordinates. Fetching....")

        embed_one = build_embed(grouped[0], grouped[1], 1)
        embed_two = build_embed(grouped[0], grouped[1], 2)
        embed_three = build_embed(grouped[0], grouped[1], 3)
        embed_four = build_embed(grouped[0], grouped[1], 4)
        embed_five = build_embed(grouped[0], grouped[1], 5)
        embed_six = build_embed(grouped[0], grouped[1], 6)

        if embed_one is not False:
            await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 1))
        if embed_two is not False:
            await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 2))
        if embed_three is not False:
            await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 3))
        if embed_four is not False:
            await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 4))
        if embed_five is not False:
            await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 5))
        if embed_six is not False:
            await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 6))


client.run(token, bot=False)
