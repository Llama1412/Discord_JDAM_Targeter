import json
import urllib.request

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
        "9M311"
    ]

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
    with urllib.request.urlopen("http://state.hoggitworld.com/") as url:
        data = json.loads(url.read().decode())
        for i in range(len(data["objects"])):
            if data["objects"][i]["Flags"]["Human"]:
                if data["objects"][i]["UnitName"] == name:
                    MyLat = data["objects"][i]["LatLongAlt"]["Lat"]
                    MyLon = data["objects"][i]["LatLongAlt"]["Long"]
    return [MyLat, MyLon]


def get_closest_site(coords):
    sites = []
    coords_list = locate_groups()
    for group in coords_list:
        calculated_distance = geopy.distance.distance(coords, group).nm
        sites.append(SITE(group[0], group[1], calculated_distance))

    sorted_sites_list = sorted(sites, key=lambda x: x.Distance)
    return sorted_sites_list[0]
