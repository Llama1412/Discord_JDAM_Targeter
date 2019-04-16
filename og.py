import urllib.request
import geopy.distance
import json
import urllib.request
import math
import geopy
import numpy as np
from scipy.cluster.hierarchy import ward, fcluster
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans


class THREAT:
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    NONE = 4
    STATIC = 5
    UNKNOWN = 6


class SERVER:
    GAW = "https://state.hoggitworld.com/f67eecc6-4659-44fd-a4fd-8816c993ad0e"


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
    "BMD-1": THREAT.NONE,
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
    "Dog Ear radar": THREAT.NONE,
    "ZIL-4331": THREAT.NONE,
    "Ural-375 PBU": THREAT.NONE,
    "BRDM-2": THREAT.NONE,
    "KAMAZ Truck": THREAT.NONE,
    "Tigr_233036": THREAT.NONE,

    "house2arm": THREAT.STATIC,
    "outpost_road": THREAT.STATIC,
    "outpost": THREAT.STATIC,
}

my_filter = [
    "FARP",
    "KUZNECOW",
    "J-11A",
    "F-5E-3",
    "Su-25T",
    "A-50",
    "An-30M",
    "Su-33",
    "MiG-31",
    "MiG-21Bis",
    "Su-27",
    "R-27ER",
    "weapons.missiles.Igla_1E",
    "9M311",
    "Mi-26"
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


class Bogey:
    def __init__(self, target_type, lat, lon, elev, dist, threat, latraw, lonraw):
        self.Type = target_type
        self.Lat = lat
        self.Lon = lon
        self.Elev = elev
        self.Dist = dist
        self.Threat = threat
        self.lat_raw = latraw
        self.lon_raw = lonraw


max_range = 5


def collect_sorted_targets(first_input, second_input):
    target_list = []
    lat_deg = int(first_input[0:2])
    lat_min = int(first_input[2:4])
    lat_sec = int(first_input[4:6])
    lat_final = float(lat_deg + (lat_min * (1 / 60)) + (lat_sec * (1 / 3600)))

    lon_deg = int(second_input[0:2])
    lon_min = int(second_input[2:4])
    lon_sec = int(second_input[4:6])
    lon_final = float(lon_deg + (lon_min * (1 / 60)) + (lon_sec * (1 / 3600)))

    with urllib.request.urlopen(SERVER.GAW) as url:
        data = json.loads(url.read().decode())
        for i in range(len(data["objects"])):
            target_pos = (lat_final, lon_final)
            if data["objects"][i]["Coalition"] == "Allies" and data["objects"][i]["Flags"]["Born"]:
                plane = data["objects"][i]
                threat = False
                enemy_type = plane["Name"]
                latitude = plane["LatLongAlt"]["Lat"]
                longitude = plane["LatLongAlt"]["Long"]
                altitude = plane["LatLongAlt"]["Alt"]
                altitude_feet = float(altitude / 0.3048)
                target_position = (latitude, longitude)
                if enemy_type not in my_filter:
                    if enemy_type in threats.keys():
                        threat = threats[enemy_type]

                    else:
                        threat = THREAT.UNKNOWN

                distance = geopy.distance.distance(target_pos, target_position).nm

                lat_d = math.floor(latitude)
                lat_m = math.floor((latitude - lat_d) * 60)
                lat_s = round((latitude - lat_d - (lat_m / 60)) * 3600)
                lat_ds = (round((latitude - lat_d - (lat_m / 60)) * 3600 * 100) / 100) - (
                    round((latitude - lat_d - (lat_m / 60)) * 3600))
                lat_ds = "{:05.2f}".format(lat_s + lat_ds)

                if float(lat_ds) >= 60:
                    lat_m = lat_m + 1
                    lat_s = lat_s - 60
                if float(lat_ds) < 0:
                    lat_m = lat_m - 1
                    lat_ds = lat_s + 60

                if lat_m >= 60:
                    lat_d = lat_d + 1
                    lat_m = lat_m - 60
                if float(lat_m) < 0:
                    lat_d = lat_d - 1
                    lat_m = lat_m + 60

                lon_d = math.floor(longitude)
                lon_m = math.floor((longitude - lon_d) * 60)
                lon_s = round((longitude - lon_d - (lon_m / 60)) * 3600)
                lon_ds = (round((longitude - lon_d - (lon_m / 60)) * 3600 * 100) / 100) - (
                    round((longitude - lon_d - (lon_m / 60)) * 3600))
                lon_ds = "{:05.2f}".format(lon_s + lon_ds)

                if float(lon_ds) >= 60:
                    lon_m = lon_m + 1
                    lon_s = lon_s - 60
                if float(lon_ds) <= 0:
                    lon_m = lon_m - 1
                    lon_ds = lon_s + 60

                if lon_m >= 60:
                    lon_d = lon_d + 1
                    lon_m = lon_m - 60
                if float(lon_m) < 0:
                    lon_d = lon_d - 1
                    lon_m = lon_m + 60

                final_lat = str("{:02d}".format(lat_d)) + "°" + str("{:02d}".format(lat_m)) + "'" + str(lat_ds) + '"'
                final_lon = str("{:02d}".format(lon_d)) + "°" + str("{:02d}".format(lon_m)) + "'" + str(lon_ds) + '"'

                lat_raw = str("{:02d}".format(lat_d))+str("{:02d}".format(lat_m))+str(lat_ds)
                lon_raw = str("{:02d}".format(lon_d))+str("{:02d}".format(lon_m))+str(lon_ds)

                if distance <= max_range and threat is not False:
                    target_list.append(Bogey(enemy_type, final_lat, final_lon, altitude_feet, distance, threat, str(int(float(lat_raw)*100)), str(int(float(lon_raw)*100))))

    sorted_target_list = sorted(target_list, key=lambda x: x.Threat)
    return sorted_target_list


def get_targets(first_input, second_input, threat_level):
    target_list = []
    lat_deg = int(first_input[0:2])
    lat_min = int(first_input[2:4])
    lat_sec = int(first_input[4:6])
    lat_final = float(lat_deg + (lat_min * (1 / 60)) + (lat_sec * (1 / 3600)))

    lon_deg = int(second_input[0:2])
    lon_min = int(second_input[2:4])
    lon_sec = int(second_input[4:6])
    lon_final = float(lon_deg + (lon_min * (1 / 60)) + (lon_sec * (1 / 3600)))

    with urllib.request.urlopen(SERVER.GAW) as url:
        data = json.loads(url.read().decode())
        for i in range(len(data["objects"])):
            target_pos = (lat_final, lon_final)
            if data["objects"][i]["Coalition"] == "Allies" and data["objects"][i]["Flags"]["Born"]:
                plane = data["objects"][i]
                threat = False
                enemy_type = plane["Name"]
                latitude = plane["LatLongAlt"]["Lat"]
                longitude = plane["LatLongAlt"]["Long"]
                altitude = plane["LatLongAlt"]["Alt"]
                altitude_feet = float(altitude / 0.3048)
                target_position = (latitude, longitude)
                if enemy_type not in my_filter:
                    if enemy_type in threats.keys():
                        threat = threats[enemy_type]

                    else:
                        threat = THREAT.UNKNOWN

                distance = geopy.distance.distance(target_pos, target_position).nm

                lat_d = math.floor(latitude)
                lat_m = math.floor((latitude - lat_d) * 60)
                lat_s = round((latitude - lat_d - (lat_m / 60)) * 3600)
                lat_ds = (round((latitude - lat_d - (lat_m / 60)) * 3600 * 100) / 100) - (
                    round((latitude - lat_d - (lat_m / 60)) * 3600))
                lat_ds = "{:05.2f}".format(lat_s + lat_ds)

                if float(lat_ds) >= 60:
                    lat_m = lat_m + 1
                    lat_s = lat_s - 60
                if float(lat_ds) < 0:
                    lat_m = lat_m - 1
                    lat_ds = lat_s + 60

                if lat_m >= 60:
                    lat_d = lat_d + 1
                    lat_m = lat_m - 60
                if float(lat_m) < 0:
                    lat_d = lat_d - 1
                    lat_m = lat_m + 60

                lon_d = math.floor(longitude)
                lon_m = math.floor((longitude - lon_d) * 60)
                lon_s = round((longitude - lon_d - (lon_m / 60)) * 3600)
                lon_ds = (round((longitude - lon_d - (lon_m / 60)) * 3600 * 100) / 100) - (
                    round((longitude - lon_d - (lon_m / 60)) * 3600))
                lon_ds = "{:05.2f}".format(lon_s + lon_ds)

                if float(lon_ds) >= 60:
                    lon_m = lon_m + 1
                    lon_s = lon_s - 60
                if float(lon_ds) <= 0:
                    lon_m = lon_m - 1
                    lon_ds = lon_s + 60

                if lon_m >= 60:
                    lon_d = lon_d + 1
                    lon_m = lon_m - 60
                if float(lon_m) < 0:
                    lon_d = lon_d - 1
                    lon_m = lon_m + 60

                final_lat = str("{:02d}".format(lat_d)) + "°" + str("{:02d}".format(lat_m)) + "'" + str(lat_ds) + '"'
                final_lon = str("{:02d}".format(lon_d)) + "°" + str("{:02d}".format(lon_m)) + "'" + str(lon_ds) + '"'
                if distance <= max_range and threat is not False and threat == threat_level:
                    target_list.append(Bogey(enemy_type, final_lat, final_lon, altitude_feet, distance, threat, 0, 0))

    # sorted_target_list = sorted(target_list, key=lambda x: x.Threat)
    return target_list

class SITE:
    def __init__(self, lat, lon, distance):
        self.lat = lat
        self.lon = lon
        self.dist = distance


def locate_groups():
    Y = []

    count = 0
    with urllib.request.urlopen("https://state.hoggitworld.com/f67eecc6-4659-44fd-a4fd-8816c993ad0e") as url:
        data = json.loads(url.read().decode())
        for i in range(len(data["objects"])):
            if data["objects"][i]["Coalition"] == "Allies" and data["objects"][i]["Flags"]["Born"] and \
                    data["objects"][i]["Name"] not in my_filter:
                plane = data["objects"][i]
                latitude = plane["LatLongAlt"]["Lat"]
                longitude = plane["LatLongAlt"]["Long"]
                Y.append([latitude, longitude])
                count = count + 1

    X = np.array(Y)

    Z = ward(pdist(X))
    max_d = 10 / 60

    clusters = fcluster(Z, max_d, criterion='distance')
    k = clusters.max() - 1
    kmeans = KMeans(n_clusters=k, precompute_distances=True)
    kmeans.fit(X)

    cluster_centers = kmeans.cluster_centers_

    return cluster_centers


def get_coords(name):
    try:
        with urllib.request.urlopen("https://state.hoggitworld.com/f67eecc6-4659-44fd-a4fd-8816c993ad0e") as url:
            data = json.loads(url.read().decode())
            for i in range(len(data["objects"])):
                if data["objects"][i]["Flags"]["Human"]:
                    if data["objects"][i]["UnitName"] == name:
                        MyLat = data["objects"][i]["LatLongAlt"]["Lat"]
                        MyLon = data["objects"][i]["LatLongAlt"]["Long"]
        return [MyLat, MyLon]
    except UnboundLocalError:
        return "error"


def get_closest_site(coords):
    sites = []
    coords_list = locate_groups()
    for group in coords_list:
        calculated_distance = geopy.distance.distance(coords, group).nm
        sites.append(SITE(group[0], group[1], calculated_distance))

    sorted_sites_list = sorted(sites, key=lambda x: x.dist)
    return sorted_sites_list[0]


def convert_position(latitude, longitude):
    lat_d = math.floor(latitude)
    lat_m = math.floor((latitude - lat_d) * 60)
    lat_s = round((latitude - lat_d - (lat_m / 60)) * 3600)
    lat_ds = (round((latitude - lat_d - (lat_m / 60)) * 3600 * 100) / 100) - (
        round((latitude - lat_d - (lat_m / 60)) * 3600))
    lat_ds = "{:05.2f}".format(lat_s + lat_ds)

    if float(lat_ds) >= 60:
        lat_m = lat_m + 1
        lat_s = lat_s - 60
    if float(lat_ds) < 0:
        lat_m = lat_m - 1
        lat_ds = lat_s + 60

    if lat_m >= 60:
        lat_d = lat_d + 1
        lat_m = lat_m - 60
    if float(lat_m) < 0:
        lat_d = lat_d - 1
        lat_m = lat_m + 60

    lon_d = math.floor(longitude)
    lon_m = math.floor((longitude - lon_d) * 60)
    lon_s = round((longitude - lon_d - (lon_m / 60)) * 3600)
    lon_ds = (round((longitude - lon_d - (lon_m / 60)) * 3600 * 100) / 100) - (
        round((longitude - lon_d - (lon_m / 60)) * 3600))
    lon_ds = "{:05.2f}".format(lon_s + lon_ds)

    if float(lon_ds) >= 60:
        lon_m = lon_m + 1
        lon_s = lon_s - 60
    if float(lon_ds) <= 0:
        lon_m = lon_m - 1
        lon_ds = lon_s + 60

    if lon_m >= 60:
        lon_d = lon_d + 1
        lon_m = lon_m - 60
    if float(lon_m) < 0:
        lon_d = lon_d - 1
        lon_m = lon_m + 60

    final_lat = str("{:02d}".format(lat_d)) + "°" + str("{:02d}".format(lat_m)) + "'" + str(lat_ds) + '"'
    final_lon = str("{:02d}".format(lon_d)) + "°" + str("{:02d}".format(lon_m)) + "'" + str(lon_ds) + '"'

    return final_lat, final_lon
