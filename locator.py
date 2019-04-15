import json
import urllib.request
import math
import geopy
import numpy as np
from scipy.cluster.hierarchy import ward, fcluster
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans



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