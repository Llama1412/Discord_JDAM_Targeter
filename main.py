import datetime
import os
import discord
from prettytable import PrettyTable

from algorithms import *
from cartridge import *
from rick import *

token = os.getenv("discord_token", False)
local = False
if token is False:
    token = "NTkwMjM2ODU0OTEwMDU4NDk3.XQfTLQ.BXMib6PVogSX8PN0A3jfRdyiuuo"
    local = True
client = discord.Client()

max_assigned = 4


def calc_time_restart(uptime):
    uptime_seconds = uptime
    time_remaining_seconds = 14400 - uptime_seconds
    return datetime.timedelta(seconds=time_remaining_seconds)


def build_embed(lat, lon, threat, server):
    target_list = get_targets(lat, lon, threat, server)
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
        int(test)
        return True
    except ValueError:
        return False


def check_valid(message):
    try:
        msg = message.content
        grouped = msg.split(" ")
        int(grouped[1])
        int(grouped[2])
        if len(grouped[1]) == 6 and len(grouped[2]) == 6:
            return True
        else:
            return False
    except ValueError:
        return False


def check_if_assign(message):
    msg = message.content
    grouped = msg.split(" ")
    if len(grouped) == 4:
        if check_if_int(grouped[3]):
            return "numbers"
        else:
            return "names"
    elif len(grouped) > 4:
        return "names"
    else:
        return False


@client.event
async def on_ready():
    print("Logged in as " + client.user.name)
    msg = "Online!"
    if local is False:
        await client.send_message(discord.Object(589952357488525332), msg)
    else:
        await client.send_message(discord.Object(590236753831657480), msg)
    return


@client.event
async def on_message(message):
    any_targets = False
    if message.author is not client:
        print(message.author.name + ": " + message.content)
    if message.author == client.user:
        return

    elif message.content.lower().startswith("help"):
        embed = discord.Embed(
            title="Help Menu",
            colour=random.randint(0, 0xffffff)
        )
        embed.add_field(name="[gaw/pgaw/cvw] <6 fig lat> <6 fig lon>",
                        value="Looks up all units in a 5nm range around the coordinates and returns their position and type.")
        embed.add_field(name="[gaw/pgaw/cvw] <6 fig lat> <6 fig lon> <list of names>",
                        value="Finds all targets around the coordinates, assigns up to 4 to each name, and then returns them, as well as formatted coords for Michae1s' JDAM entry tool.")
        embed.add_field(name="[gaw/pgaw/cvw] lookup <exact ingame name>",
                        value="Looks up the target user and returns the nearest group of enemies to them.")
        embed.add_field(name="list [gaw/pgaw/cvw]",
                        value="Prints a list of all users on the selected server and which aircraft they are flying.")
        embed.add_field(name="limit [number]",
                        value="Changes the limit of targets assigned per person.")
        embed.add_field(name="help",
                        value="Shows this menu.")
        await client.send_message(message.channel, embed=embed)

    elif len(message.content.lower().split(" ")) > 1:
        if message.content.lower().startswith("rick"):
            split = message.content.split(" ")
            try:
                words = int(split[1])
                syl = int(split[2])
                msg = name_creator(words, syl)
                await client.send_message(message.channel, msg)
            except ValueError:
                await client.send_message(message.channel, "Those numbers weren't legit, bud.")

        elif message.content.lower().startswith("limit"):
            global max_assigned
            try:
                number = int(message.content.split(" ")[1])
                max_assigned = number
                msg = "Maximum targets changed to " + str(number) + "."
                await client.send_message(message.channel, msg)
            except TypeError:
                msg = "That isn't a valid number."
                await client.send_message(message.channel, msg)

        elif message.content.lower().startswith("list"):
            server_address = None
            if message.content.lower().split(" ")[1] == "gaw":
                server_address = SERVER.GAW
            elif message.content.lower().split(" ")[1] == "pgaw":
                server_address = SERVER.PGAW
            elif message.content.lower().split(" ")[1] == "cvw":
                server_address = SERVER.CVW
            if server_address is not None:
                count = 0
                people = []
                y = PrettyTable()
                y.field_names = ["Name", "Aircraft"]
                with urllib.request.urlopen(server_address) as url:
                    found_data = json.loads(url.read().decode())
                    playercount = int(found_data["players"] - 1)
                    maxplayers = int(found_data["maxPlayers"] - 1)
                    servername = found_data["serverName"]
                    ttr = calc_time_restart(found_data["uptime"])
                    for i in range(len(found_data["objects"])):
                        if found_data["objects"][i]["Flags"]["Human"]:
                            count = count + 1
                            name = str(found_data["objects"][i]["UnitName"])
                            plane = str(found_data["objects"][i]["Name"])
                            people.append(Player(name, plane))
                sorted_people = sorted(people, key=lambda x: x.Plane)
                for player in sorted_people:
                    y.add_row([player.Name, player.Plane])
                y.align["Name"] = "l"
                y.align["Aircraft"] = "l"
                msg = "There are currently " + str(playercount) + " out of " + str(maxplayers) + " connected to " + str(
                    servername) + "```\n" + str(y) + "\n```\n Time until restart:   " + str(ttr)
                await client.send_message(message.channel, msg)

        elif message.content.lower().split(" ")[1].startswith("lookup"):
            servername = message.content.lower().split(" ")[0]
            server = ""
            if servername == "pgaw":
                server = SERVER.PGAW
            elif servername == "gaw":
                server = SERVER.GAW
            elif servername == "cvw":
                server = SERVER.CVW

            splitup = message.content.split(" ")
            name = " ".join(splitup[2:])

            name_coords, target_name = get_coords(name, server)

            if name_coords == "error":
                await client.send_message(message.channel, name + " isn't a user in the server.")

            else:
                await client.send_message(message.channel, "Searching for sites near " + str(target_name) + str("."))
                closest_sites = get_closest_site(name_coords, server)
                embed = discord.Embed(
                    title="Closest enemy sites for " + str(name),
                    colour=random.randint(0, 0xffffff)
                )
                for site in closest_sites:
                    final_lat, final_lon = convert_position(site.lat, site.lon)
                    embed.add_field(name="Range: " + str(round(site.dist, 2)) + "nm",
                                    value="Lat:   " + str(final_lat) + "\nLon:   " + str(
                                        final_lon) + "\n" + str(site.targets) + " targets.")
                await client.send_message(message.channel, embed=embed)

        elif message.content.lower().startswith("gaw"):
            if check_valid(message):
                if check_if_assign(message) == "names":
                    grouped = message.content.split(" ")
                    print("Detected Lat: " + str(grouped[1]))
                    print("Detected Lon: " + str(grouped[2]))
                    await client.send_message(message.channel,
                                              "Those are valid coordinates with individual targets assigned. Fetching....")

                    grouped = message.content.split(" ")
                    list_of_names = grouped[3:]
                    list_of_targets = collect_sorted_targets(grouped[1], grouped[2], SERVER.GAW)

                    maximum_targets = math.floor(len(list_of_targets) / max_assigned)
                    remainder = len(list_of_targets) % max_assigned
                    count = 0

                    for name in list_of_names:
                        list_of_crap = []
                        if count < maximum_targets:
                            targets_for_person = list_of_targets[
                                                 max_assigned * count:(max_assigned * count) + max_assigned]
                            embed = discord.Embed(
                                title="Targets for " + name,
                                description=str(len(targets_for_person)) + "/" + str(max_assigned) + " targets shown.",
                                colour=random.randint(0, 0xffffff)
                            )
                            for bogey in targets_for_person:
                                embed.add_field(name=bogey.Type,
                                                value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                                    round(bogey.Elev)) + "ft\nDist:   " + str(
                                                    round(bogey.Dist, 4)) + "\n",
                                                inline=True)
                                list_of_crap.append(
                                    bogey.lat_raw + "\n" + bogey.lon_raw + "\n" + str(round(bogey.Elev)) + "\n")

                            # embed.add_field(name="Michae1s",
                            #               value="".join(list_of_crap),
                            #              inline=True)
                            await client.send_message(message.channel, embed=embed)
                            create_cartridge(targets_for_person)
                            await client.send_file(message.channel, open("output.json", "r+"), filename="output.json")
                            count = count + 1
                        elif count == maximum_targets:
                            targets_for_person = list_of_targets[
                                                 max_assigned * count:(max_assigned * count) + remainder]
                            embed = discord.Embed(
                                title="Targets for " + name,
                                description=str(len(targets_for_person)) + "/" + str(max_assigned) + " targets shown.",
                                colour=random.randint(0, 0xffffff)
                            )
                            if len(targets_for_person) != 0:
                                for bogey in targets_for_person:
                                    embed.add_field(name=bogey.Type,
                                                    value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                                        round(bogey.Elev)) + "ft\nDist:   " + str(
                                                        round(bogey.Dist, 4)) + "\n",
                                                    inline=True)
                                    list_of_crap.append(
                                        bogey.lat_raw + "\n" + bogey.lon_raw + "\n" + str(round(bogey.Elev)) + "\n")
                                # embed.add_field(name="Michae1s",
                                #               value="".join(list_of_crap),
                                #              inline=True)
                                await client.send_message(message.channel, embed=embed)
                                create_cartridge(targets_for_person)
                                await client.send_file(message.channel, open("output.json", "r+"),
                                                       filename="output.json")
                            count = count + 1

                else:
                    grouped = message.content.split(" ")
                    print("Detected Lat: " + str(grouped[1]))
                    print("Detected Lon: " + str(grouped[2]))
                    await client.send_message(message.channel, "Those are valid coordinates. Fetching....")

                    embed_one = build_embed(grouped[1], grouped[2], 1, SERVER.GAW)
                    embed_two = build_embed(grouped[1], grouped[2], 2, SERVER.GAW)
                    embed_three = build_embed(grouped[1], grouped[2], 3, SERVER.GAW)
                    embed_four = build_embed(grouped[1], grouped[2], 4, SERVER.GAW)
                    embed_five = build_embed(grouped[1], grouped[2], 5, SERVER.GAW)
                    embed_six = build_embed(grouped[1], grouped[2], 6, SERVER.GAW)

                    if embed_one is not False:
                        await client.send_message(message.channel, embed=embed_one)
                        any_targets = True
                    if embed_two is not False:
                        await client.send_message(message.channel, embed=embed_two)
                        any_targets = True
                    if embed_three is not False:
                        await client.send_message(message.channel, embed=embed_three)
                        any_targets = True
                    if embed_four is not False:
                        await client.send_message(message.channel, embed=embed_four)
                        any_targets = True
                    if embed_five is not False:
                        await client.send_message(message.channel, embed=embed_five)
                        any_targets = True
                    if embed_six is not False:
                        await client.send_message(message.channel, embed=embed_six)
                        any_targets = True

                    if any_targets is False:
                        await client.send_message(message.channel,
                                                  content="There were no targets detected within 5nm of that point.")
        elif message.content.lower().startswith("pgaw"):
            if check_valid(message):
                if check_if_assign(message) == "names":
                    grouped = message.content.split(" ")
                    print("Detected Lat: " + str(grouped[1]))
                    print("Detected Lon: " + str(grouped[2]))
                    await client.send_message(message.channel,
                                              "Those are valid coordinates with individual targets assigned. Fetching....")

                    grouped = message.content.split(" ")
                    list_of_names = grouped[3:]
                    list_of_targets = collect_sorted_targets(grouped[1], grouped[2], SERVER.PGAW)

                    maximum_targets = math.floor(len(list_of_targets) / max_assigned)
                    remainder = len(list_of_targets) % max_assigned
                    count = 0

                    for name in list_of_names:
                        list_of_crap = []
                        if count < maximum_targets:
                            targets_for_person = list_of_targets[
                                                 max_assigned * count:(max_assigned * count) + max_assigned]
                            embed = discord.Embed(
                                title="Targets for " + name,
                                description=str(len(targets_for_person)) + "/" + str(max_assigned) + " targets shown.",
                                colour=random.randint(0, 0xffffff)
                            )
                            for bogey in targets_for_person:
                                embed.add_field(name=bogey.Type,
                                                value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                                    round(bogey.Elev)) + "ft\nDist:   " + str(
                                                    round(bogey.Dist, 4)) + "\n",
                                                inline=True)
                                list_of_crap.append(
                                    bogey.lat_raw + "\n" + bogey.lon_raw + "\n" + str(round(bogey.Elev)) + "\n")

                            # embed.add_field(name="Michae1s",
                            #                 value="".join(list_of_crap),
                            #                 inline=True)
                            await client.send_message(message.channel, embed=embed)
                            create_cartridge(targets_for_person)
                            await client.send_file(message.channel, open("output.json", "r+"), filename="output.json")
                            count = count + 1
                        elif count == maximum_targets:
                            targets_for_person = list_of_targets[
                                                 max_assigned * count:(max_assigned * count) + remainder]
                            embed = discord.Embed(
                                title="Targets for " + name,
                                description=str(len(targets_for_person)) + "/" + str(max_assigned) + " targets shown.",
                                colour=random.randint(0, 0xffffff)
                            )
                            if len(targets_for_person) != 0:
                                for bogey in targets_for_person:
                                    embed.add_field(name=bogey.Type,
                                                    value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                                        round(bogey.Elev)) + "ft\nDist:   " + str(
                                                        round(bogey.Dist, 4)) + "\n",
                                                    inline=True)
                                    list_of_crap.append(
                                        bogey.lat_raw + "\n" + bogey.lon_raw + "\n" + str(round(bogey.Elev)) + "\n")
                                # embed.add_field(name="Michae1s",
                                #                 value="".join(list_of_crap),
                                #                 inline=True)
                                await client.send_message(message.channel, embed=embed)
                                create_cartridge(targets_for_person)
                                await client.send_file(message.channel, open("output.json", "r+"),
                                                       filename="output.json")
                            count = count + 1

                else:
                    grouped = message.content.split(" ")
                    print("Detected Lat: " + str(grouped[1]))
                    print("Detected Lon: " + str(grouped[2]))
                    await client.send_message(message.channel, "Those are valid coordinates. Fetching....")

                    embed_one = build_embed(grouped[1], grouped[2], 1, SERVER.PGAW)
                    embed_two = build_embed(grouped[1], grouped[2], 2, SERVER.PGAW)
                    embed_three = build_embed(grouped[1], grouped[2], 3, SERVER.PGAW)
                    embed_four = build_embed(grouped[1], grouped[2], 4, SERVER.PGAW)
                    embed_five = build_embed(grouped[1], grouped[2], 5, SERVER.PGAW)
                    embed_six = build_embed(grouped[1], grouped[2], 6, SERVER.PGAW)

                    if embed_one is not False:
                        await client.send_message(message.channel, embed=embed_one)
                        any_targets = True
                    if embed_two is not False:
                        await client.send_message(message.channel, embed=embed_two)
                        any_targets = True
                    if embed_three is not False:
                        await client.send_message(message.channel, embed=embed_three)
                        any_targets = True
                    if embed_four is not False:
                        await client.send_message(message.channel, embed=embed_four)
                        any_targets = True
                    if embed_five is not False:
                        await client.send_message(message.channel, embed=embed_five)
                        any_targets = True
                    if embed_six is not False:
                        await client.send_message(message.channel, embed=embed_six)
                        any_targets = True

                    if any_targets is False:
                        await client.send_message(message.channel,
                                                  content="There were no targets detected within 5nm of that point.")
        elif message.content.lower().startswith("cvw"):
            if check_valid(message):
                if check_if_assign(message) == "names":
                    grouped = message.content.split(" ")
                    print("Detected Lat: " + str(grouped[1]))
                    print("Detected Lon: " + str(grouped[2]))
                    await client.send_message(message.channel,
                                              "Those are valid coordinates with individual targets assigned. Fetching....")

                    grouped = message.content.split(" ")
                    list_of_names = grouped[3:]
                    list_of_targets = collect_sorted_targets(grouped[1], grouped[2], SERVER.CVW)

                    maximum_targets = math.floor(len(list_of_targets) / max_assigned)
                    remainder = len(list_of_targets) % max_assigned
                    count = 0

                    for name in list_of_names:
                        list_of_crap = []
                        if count < maximum_targets:
                            targets_for_person = list_of_targets[
                                                 max_assigned * count:(max_assigned * count) + max_assigned]
                            embed = discord.Embed(
                                title="Targets for " + name,
                                description=str(len(targets_for_person)) + "/" + str(max_assigned) + " targets shown.",
                                colour=random.randint(0, 0xffffff)
                            )
                            for bogey in targets_for_person:
                                embed.add_field(name=bogey.Type,
                                                value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                                    round(bogey.Elev)) + "ft\nDist:   " + str(
                                                    round(bogey.Dist, 4)) + "\n",
                                                inline=True)
                                list_of_crap.append(
                                    bogey.lat_raw + "\n" + bogey.lon_raw + "\n" + str(round(bogey.Elev)) + "\n")

                            # embed.add_field(name="Michae1s",
                            #                 value="".join(list_of_crap),
                            #                 inline=True)
                            await client.send_message(message.channel, embed=embed)
                            create_cartridge(targets_for_person)
                            await client.send_file(message.channel, open("output.json", "r+"), filename="output.json")
                            count = count + 1
                        elif count == maximum_targets:
                            targets_for_person = list_of_targets[
                                                 max_assigned * count:(max_assigned * count) + remainder]
                            embed = discord.Embed(
                                title="Targets for " + name,
                                description=str(len(targets_for_person)) + "/" + str(max_assigned) + " targets shown.",
                                colour=random.randint(0, 0xffffff)
                            )
                            if len(targets_for_person) != 0:
                                for bogey in targets_for_person:
                                    embed.add_field(name=bogey.Type,
                                                    value="Lat:   " + bogey.Lat + "\nLon:   " + bogey.Lon + "\nAlt:   " + str(
                                                        round(bogey.Elev)) + "ft\nDist:   " + str(
                                                        round(bogey.Dist, 4)) + "\n",
                                                    inline=True)
                                    list_of_crap.append(
                                        bogey.lat_raw + "\n" + bogey.lon_raw + "\n" + str(round(bogey.Elev)) + "\n")
                                # embed.add_field(name="Michae1s",
                                #                 value="".join(list_of_crap),
                                #                 inline=True)
                                await client.send_message(message.channel, embed=embed)
                                create_cartridge(targets_for_person)
                                await client.send_file(message.channel, open("output.json", "r+"),
                                                       filename="output.json")
                            count = count + 1

                else:
                    grouped = message.content.split(" ")
                    print("Detected Lat: " + str(grouped[1]))
                    print("Detected Lon: " + str(grouped[2]))
                    await client.send_message(message.channel, "Those are valid coordinates. Fetching....")

                    embed_one = build_embed(grouped[1], grouped[2], 1, SERVER.CVW)
                    embed_two = build_embed(grouped[1], grouped[2], 2, SERVER.CVW)
                    embed_three = build_embed(grouped[1], grouped[2], 3, SERVER.CVW)
                    embed_four = build_embed(grouped[1], grouped[2], 4, SERVER.CVW)
                    embed_five = build_embed(grouped[1], grouped[2], 5, SERVER.CVW)
                    embed_six = build_embed(grouped[1], grouped[2], 6, SERVER.CVW)

                    if embed_one is not False:
                        await client.send_message(message.channel, embed=embed_one)
                        any_targets = True
                    if embed_two is not False:
                        await client.send_message(message.channel, embed=embed_two)
                        any_targets = True
                    if embed_three is not False:
                        await client.send_message(message.channel, embed=embed_three)
                        any_targets = True
                    if embed_four is not False:
                        await client.send_message(message.channel, embed=embed_four)
                        any_targets = True
                    if embed_five is not False:
                        await client.send_message(message.channel, embed=embed_five)
                        any_targets = True
                    if embed_six is not False:
                        await client.send_message(message.channel, embed=embed_six)
                        any_targets = True

                    if any_targets is False:
                        await client.send_message(message.channel,
                                                  content="There were no targets detected within 5nm of that point.")


def runner():
    try:
        client.run(token)
    except:
        runner()


runner()
