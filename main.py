import copy
import json

import pandas as pd
import random
import math
import numpy as np

df = pd.read_excel('Review_ratings.xlsx')
data = {}
user = 0
threshold = float(input("Enter the threshold distance for determining the outliers"))
for ind, row in df.iterrows():
    user += 1
    categories = [
        row['Category 1'],
        row['Category 2'],
        row['Category 3'],
        row['Category 4'],
        row['Category 5'],
        row['Category 6'],
        row['Category 7'],
        row['Category 8'],
        row['Category 9'],
        row['Category 10'],
        row['Category 11'],
        row['Category 12'],
        row['Category 13'],
        row['Category 14'],
        row['Category 15'],
        row['Category 16'],
        row['Category 17'],
        row['Category 18'],
        row['Category 19'],
        row['Category 20'],
        row['Category 21'],
        row['Category 22'],
        row['Category 23'],
        row['Category 24'],
    ]
    data[user] = categories

list1 = [0, 0, 3.63, 3.65, 5, 2.92, 5, 2.35, 2.33, 2.64, 1.7, 1.69, 1.7, 1.72, 1.74, 0.59, 0.5, 0, 0.5, 0, 0, 0, 0, 0]
list45 = [0.57, 0.58, 5, 3.73, 3.78, 2.95, 2.94, 2.96, 1.63, 1.63, 5, 1.55, 1.54, 1.55, 1.18, 0.69, 0.58, 0, 0, 0, 0.54,
          0.53, 0.53, 0.58]


def pick_initial_centroid(k):  # returns random centroids {'C123':[x,y,....,z]} used as initial centroids
    points = random.sample(range(1, 1001), k)
    # points = [470, 159, 502]
    lis = {}
    for point in points:
        name = "C" + str(point)
        lis[name] = data[point]
    return lis


def distance_between_categories(centroid, point):  # distance between 2 points
    distance = 0.0
    for i in range(len(point)):
        distance += (float(centroid[i]) - point[i]) ** 2
    return math.sqrt(distance)


def calculate_distances_of_data(centroids):  # calculate the distances centroids and all the points in the data set
    # returns all the points as key and list of dictionaries of the distances between the centroids
    distances = {}
    for user_, point in data.items():
        distance_list = []
        for key, centroid in centroids.items():
            distance_list.append({key: distance_between_categories(centroid, point)})
        distances[user_] = distance_list
    return distances


def min_index(list_x):  # returns the index of minimum number in a list
    return int(np.where(list_x == np.min(list_x))[0])


def get_dict_with_min_value(dict_list):
    if not dict_list:
        return None
    return min(dict_list, key=lambda x: list(x.values())[0])


def get_key_with_min_value(dict_list):  # returns the centroid (key) which the point is closest to
    min_dict = get_dict_with_min_value(dict_list)
    outlier = False
    if list(min_dict.values())[0] > threshold:
        outlier = True
    return list(min_dict.keys())[0], outlier


def cluster(distances, centroids):  # cluster all the points around the centroids
    outliers = {}
    cluster_dict = {}
    for key, centroid in centroids.items():
        cluster_dict[key] = []
        outliers[key] = []
    for user_id, distance in distances.items():
        selected_centroid, is_outlier = get_key_with_min_value(distance)
        cluster_dict[selected_centroid].append({user_id: data[user_id]})
        if is_outlier:
            outliers[selected_centroid].append(user_id)

    return cluster_dict, outliers


def calculate_average_point(list_of_points, centroid):
    """
    @:parameter list_of_points which is dictionary of points that belongs to certain cluster with key
                as the number of the entry and value is list of 24 dimensions

                gets the average dimension between all the dimensions

    @:returns list of the new 24 dimensions of the new cluster

    """
    output = []
    points = []
    for dic in list_of_points:
        key, value = dic.popitem()
        if key != int(centroid):
            points.append(value)
    length = len(points)
    for i in range(24):
        new_coordinate = 0
        for point in points:
            new_coordinate = new_coordinate + point[i]
        new_coordinate = new_coordinate / length
        new_coordinate = "{:.2f}".format(new_coordinate)
        output.append(new_coordinate)

    return output


def calculate_new_centroids(clusters):  # get the new centroids
    new_centroids = {}
    copy_of_clusters = copy.deepcopy(clusters)
    for centroid, points in copy_of_clusters.items():
        new_centroids[centroid] = calculate_average_point(points, centroid[1:])
    return new_centroids


def is_similar(list_1, list_2):  # returns true if 2 lists are similar
    if list_1 == list_2:
        return True
    else:
        return False


def needs_iteration(old_cluster, new_cluster, centroids):
    """ ALGORITHM:
        takes a dictionary of centroids as key and list of dictionaries as value
        -> checks if the keys of each cluster are the same if YES return FALSE
                                                        -> if NO return TRUE
    """

    centroids_list = list(centroids.keys())
    cluster_old = copy.deepcopy(old_cluster)
    cluster_new = copy.deepcopy(new_cluster)
    #  gets the keys of the cluster
    old = []
    new = []

    for centroid in centroids_list:
        old_temp_list = []
        new_temp_list = []
        for dic in cluster_old[centroid]:
            key, value = dic.popitem()
            old_temp_list.append(key)
        for dic in cluster_new[centroid]:
            key,value = dic.popitem()
            new_temp_list.append(key)
        old.append(sorted(old_temp_list))
        new.append(sorted(new_temp_list))
    if is_similar(old, new):
        return False
    else:
        return True


def k_means():
    centroids = pick_initial_centroid(3)
    distances = calculate_distances_of_data(centroids)
    clusters,outliers = cluster(distances, centroids)
    while True:
        new_centroids = calculate_new_centroids(clusters)
        new_distances = calculate_distances_of_data(new_centroids)
        new_clusters, outliers = cluster(new_distances, new_centroids)
        if needs_iteration(clusters, new_clusters, new_centroids):
            clusters = new_clusters
        else:
            break
    return new_clusters, outliers


clusters_, outliers_ = k_means()

print("clusters: ")
print(json.dumps(clusters_))
print()
print("outliers:")
print(json.dumps(outliers_))


