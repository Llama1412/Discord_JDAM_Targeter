def create_cartridge(targets):
    with open("cartridge.txt", "w+") as f:
        count = 0
        f.write("cartridgename = Llama's JDAM Bot")

        for bogey in targets:
            f.write("\n\n")
            count = count + 1
            data = ["[B" + str(count) + "]", "latitude = " + str(bogey.lat_full), "longitude = " + str(bogey.lon_full),
                    "missiontime = 0", "velocity = 0", "etalocked = false", "velocitylocked = false",
                    "istargetpoint = true"]

            to_write = str("\n".join(data))
            f.write(to_write)
