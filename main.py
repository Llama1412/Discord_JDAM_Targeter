import random
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


def check_if_int(test):
    try:
        check = int(test)
        return True
    except ValueError:
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


def check_if_assign(message):
    msg = message.content
    grouped = msg.split(" ")
    if len(grouped) == 3:
        if check_if_int(grouped[2]):
            return "numbers"
        else:
            return "names"
    elif len(grouped) > 3:
        return "names"
    else:
        return False


@client.event
async def on_ready():
    print("Logged in as " + client.user.name)
    return


@client.event
async def on_message(message):
    any_targets = False
    if message.author is not client:
        print(message.author.name + ": " + message.content)
    if message.author == client.user:
        return

    elif message.content.startswith("lookup"):
        splitup = message.content.split(" ")
        name = " ".join(splitup[1:])
        print("Triggered lookup for "+str(name))
        name_coords = get_coords(name)

        if name_coords == "error":
            await client.send_message(message.channel, name+" isn't a user in the server.")

        else:
            closest_site = get_closest_site(name_coords)

            final_lat, final_lon = convert_position(closest_site.lat, closest_site.lon)
            embed = discord.Embed(
                title="Closest enemy site for " + str(name),
                colour=random.randint(0, 0xffffff)
            )
            embed.add_field(name="Range: "+str(round(closest_site.dist,2))+"nm",
                            value="Lat:   " + str(final_lat) + "\nLon:   " + str(final_lon))
            await client.send_message(message.channel, embed=embed)

    elif check_valid(message):
        if check_if_assign(message) == "names":
            grouped = message.content.split(" ")
            print("Detected Lat: " + str(grouped[0]))
            print("Detected Lon: " + str(grouped[1]))
            await client.send_message(message.channel,
                                      "Those are valid coordinates with individual targets assigned. Fetching....")

            grouped = message.content.split(" ")
            list_of_names = grouped[2:]
            list_of_targets = collect_sorted_targets(grouped[0], grouped[1])

            maximum_targets = math.floor(len(list_of_targets) / 4)
            remainder = len(list_of_targets) % 4
            count = 0

            for name in list_of_names:
                if count < maximum_targets:
                    targets_for_person = list_of_targets[4 * count:(4 * count) + 4]
                    embed = discord.Embed(
                        title="Targets for " + name,
                        description=str(len(targets_for_person)) + "/4 targets shown.",
                        colour=random.randint(0, 0xffffff)
                    )
                    for bogey in targets_for_person:
                        embed.add_field(name=bogey.Type,
                                        value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                            round(bogey.Elev)) + "ft\nDist:   " + str(round(bogey.Dist, 4)) + "\n",
                                        inline=True)

                    await client.send_message(message.channel, embed=embed)
                    count = count + 1
                elif count == maximum_targets:
                    targets_for_person = list_of_targets[4 * count:(4 * count) + remainder]
                    embed = discord.Embed(
                        title="Targets for " + name,
                        description=str(len(targets_for_person)) + "/4 targets shown.",
                        colour=random.randint(0, 0xffffff)
                    )
                    if len(targets_for_person) != 0:
                        for bogey in targets_for_person:
                            embed.add_field(name=bogey.Type,
                                            value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                                round(bogey.Elev)) + "ft\nDist:   " + str(round(bogey.Dist, 4)) + "\n",
                                            inline=True)

                        await client.send_message(message.channel, embed=embed)
                    count = count + 1

        else:
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
                any_targets = True
            if embed_two is not False:
                await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 2))
                any_targets = True
            if embed_three is not False:
                await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 3))
                any_targets = True
            if embed_four is not False:
                await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 4))
                any_targets = True
            if embed_five is not False:
                await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 5))
                any_targets = True
            if embed_six is not False:
                await client.send_message(message.channel, embed=build_embed(grouped[0], grouped[1], 6))
                any_targets = True

            if any_targets is False:
                await client.send_message(message.channel,
                                          content="There were no targets detected within 5nm of that point.")


client.run(token, bot=False)
