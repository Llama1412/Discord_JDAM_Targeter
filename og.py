import urllib.request
import json
import math
import geopy.distance
from prettytable import PrettyTable
from termcolor import colored
import pyfiglet

ascii_banner = pyfiglet.figlet_format("JDAM Targeter")
print(colored(ascii_banner, "cyan"))
print(colored(
    "Decide where you want to attack and enter the Lat and Lon for the target area. The program will then identify all ground targets within 5 miles of it.\n",
    "cyan"))

x = PrettyTable()
x.field_names = ["Unit Name", "Latitude", "Longitude", "Elevation", "Distance"]
height_offset = 5


class THREAT:
    HIGH = "red"
    MEDIUM = "yellow"
    LOW = "green"
    NONE = "blue"
    STATIC = "cyan"
    UNKNOWN = "white"


threats = {
    "2S6 Tunguska": THREAT.HIGH,
    "SA-11 Buk LN 9A310M1": THREAT.HIGH,
    "Tor 9A331": THREAT.HIGH,
    "SA-11 Buk SR 9S18M1": THREAT.HIGH,
    "SA-11 Buk CC 9S470M1": THREAT.HIGH,
    "Osa 9A33 ln": THREAT.HIGH,
    "Strela-10M3": THREAT.HIGH,
    "Strela-1 9P31": THREAT.HIGH,
    "5p73 s-125 ln": THREAT.HIGH,
    "Kub 2P25 ln": THREAT.HIGH,
    "snr s-125 tr": THREAT.HIGH,
    "S-300PS 40B6M tr": THREAT.HIGH,
    "S-300PS 40B6MD sr": THREAT.HIGH,
    "S-300PS 5P85D ln": THREAT.HIGH,
    "S-300PS 64H6E sr": THREAT.HIGH,
    "S-300PS 5P85C ln": THREAT.HIGH,
    "p-19 s-125 sr": THREAT.HIGH,
    "S_75M_Volhov": THREAT.HIGH,
    "Kub 1S91 str": THREAT.HIGH,
    "SNR_75V": THREAT.HIGH,

    "SA-18 Igla-S manpad": THREAT.MEDIUM,

    "Ural-375 ZU-23": THREAT.LOW,
    "ZU-23 Emplacement Closed": THREAT.LOW,
    "ZU-23 Emplacement": THREAT.LOW,
    "ZSU-23-4 Shilka": THREAT.LOW,

    "BMP-1": THREAT.NONE,
    "SAU Msta": THREAT.NONE,
    "Infantry AK": THREAT.NONE,
    "SA-18 Igla-S comm": THREAT.NONE,
    "T-72B": THREAT.NONE,
    "BTR-80": THREAT.NONE,
    "BMP-3": THREAT.NONE,
    "SKP-11": THREAT.NONE,
    "1L13 EWR": THREAT.NONE,
    "ATZ-10": THREAT.NONE,
    "S-300PS 54K6 cp": THREAT.NONE,
    "BMP-2": THREAT.NONE,

    "FARP": THREAT.STATIC,
    "house2arm": THREAT.STATIC,
    "outpost_road": THREAT.STATIC,
    "outpost": THREAT.STATIC,
}

aircraft = [
    "J-11A",
    "F-5E-3",
    "Su-25T",
    "A-50",
    "An-30M"
]


def calculate_initial_compass_bearing(point_a, point_b):
    lat1 = math.radians(point_a[0])
    lat2 = math.radians(point_b[0])
    diff_long = math.radians(point_b[1] - point_a[1])
    x = math.sin(diff_long) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                           * math.cos(lat2) * math.cos(diff_long))
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing


first_input = input(colored("Enter Lat:\t", "yellow"))
# first_input = "431503"
second_input = input(colored("Enter Lon:\t", "yellow"))
# second_input = "401909"


lat_deg = int(first_input[0:2])
lat_min = int(first_input[2:4])
lat_sec = int(first_input[4:6])
lat_final = float(lat_deg + (lat_min * (1 / 60)) + (lat_sec * (1 / 3600)))

lon_deg = int(second_input[0:2])
lon_min = int(second_input[2:4])
lon_sec = int(second_input[4:6])
lon_final = float(lon_deg + (lon_min * (1 / 60)) + (lon_sec * (1 / 3600)))
# print(str(lat_final)+" "+str(lon_final))


with urllib.request.urlopen("https://state.hoggitworld.com/f67eecc6-4659-44fd-a4fd-8816c993ad0e") as url:
    data = json.loads(url.read().decode())
    onscreen = 0
    for i in range(len(data["objects"])):
        TargPos = (lat_final, lon_final)
        if data["objects"][i]["Coalition"] == "Allies" and data["objects"][i]["Flags"]["Born"]:
            plane = data["objects"][i]
            Threat = False
            Type = plane["Name"]
            Lat = plane["LatLongAlt"]["Lat"]
            Lon = plane["LatLongAlt"]["Long"]
            Alt = plane["LatLongAlt"]["Alt"]
            AltFeet = float(Alt / 0.3048)
            TPos = (Lat, Lon)
            if Type not in aircraft:
                if Type in threats.keys():
                    Threat = threats[Type]

                else:
                    Threat = THREAT.UNKNOWN

            Distance = geopy.distance.distance(TargPos, TPos).nm

            A = (lon_final, lon_final)
            B = (Lat, Lon)
            Bearing = calculate_initial_compass_bearing(A, B)
            # print(Distance)
            lat_d = math.floor(Lat)
            lat_m = math.floor((Lat - lat_d) * 60)
            lat_s = round((Lat - lat_d - (lat_m / 60)) * 3600)
            lat_ds = (round((Lat - lat_d - (lat_m / 60)) * 3600 * 100) / 100) - (
                round((Lat - lat_d - (lat_m / 60)) * 3600))
            lat_ds = "{:05.2f}".format(lat_s + lat_ds)

            if lat_s == 60:
                lat_m = lat_m + 1
            if lat_m == 60:
                lat_d = lat_d + 1

            lon_d = math.floor(Lon)
            lon_m = math.floor((Lon - lon_d) * 60)
            lon_s = round((Lon - lon_d - (lon_m / 60)) * 3600)
            lon_ds = (round((Lon - lon_d - (lon_m / 60)) * 3600 * 100) / 100) - (
                round((Lon - lon_d - (lon_m / 60)) * 3600))
            lon_ds = "{:05.2f}".format(lon_s + lon_ds)

            if lon_s == 60:
                lon_m = lon_m + 1
            if lon_m == 60:
                lon_d = lon_d + 1

            if Distance <= 5 and Threat != False:
                x.add_row([colored(Type, Threat),
                           colored(str("{:02d}".format(lat_d)) + "°" + str("{:02d}".format(lat_m)) + "'" + str(
                               lat_ds) + '"', Threat),
                           colored(str("{:02d}".format(lon_d)) + "°" + str("{:02d}".format(lon_m)) + "'" + str(
                               lon_ds) + '"', Threat),
                           colored(str(round(AltFeet) + height_offset) + "ft", Threat),
                           colored(str(round(Distance, 4)) + "nm", Threat)])
print(x)
