import json


class Point:
    def __init__(self, lat, lon, elev, name, station):
        self.latitude = lat
        self.longitude = lon
        self.elevation = elev
        self.name = name
        self.station = station

    def get(self):
        output = {"latitude": self.latitude,
                  "longitude": self.longitude,
                  "elevation": self.elevation,
                  "name": self.name,
                  "sequence": 0,
                  "wp_type": "MSN",
                  "station": self.station}
        return output


def create_cartridge(targets):
    my_list = {"waypoints": [],
               "name": "",
               "aircraft": "hornet"}
    stations = [2, 3, 7, 8]
    points = []
    count = 0
    for bogey in targets:
        if count is 4:
            count = 0
        my_station = stations[count]
        points.append(Point(bogey.lat_full, bogey.lon_full, bogey.Elev, bogey.Type, my_station).get())
        count += 1

    my_list["waypoints"] = points
    with open('output.json', 'w') as json_file:
        json.dump(my_list, json_file, indent=4, separators=(',', ': '))

    # create_cartridge(targets_for_person)
    # await client.send_file(message.channel, open("cartridge.txt", "r+"), filename="CustomCartridge.ini")
