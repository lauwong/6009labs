#!/usr/bin/env python3

import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}


def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)

    Parameters:
        nodes_filename (string): the path to the file containing the map nodes
        ways_filename (string) : the path to the file containing the map ways

    Returns:
        node_map (dict): a map of all node indexes and indexes of their neighbors
            * key (int) : a node ID
            * value (list) : all neighboring nodes
        node_coords (dict) : a reference of all node IDs and corresponding locs
            * key (int) : a node ID
            * value (tuple) : a tuple containing the corresponding latitude
                and longitude as (lat, lon)
        cost_map (dict) : a map of paths between two neighboring nodes, and the
            associated distance and time cost of traversal
            * key (tuple) : (node ID, neighboring node ID)
            * value (tuple) : distance and time cost as (dist, time)

    """

    valid_ways = []
    valid_nodes = set()
    node_coords = {}
    node_map = {}
    cost_map = {}

    # Gets all ways of the highway type and associated nodes
    # and adds them to a list of valid ways and nodes
    for way in read_osm_data(ways_filename):
        if 'highway' in way['tags']:
            if way['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                valid_ways.append(way)
                valid_nodes.update(way['nodes'])

    # Fills node_coords with id:(lat,lon) items
    for node in read_osm_data(nodes_filename):
        if node['id'] in valid_nodes:
            node_coords[node['id']] = (node['lat'], node['lon'])

    for way in valid_ways:
        tags = way['tags']
        nodes_list = way['nodes']
        twoway = (tags.get('oneway') != 'yes')

        # Iterates through each node in the way
        for n in range(len(nodes_list)-1):
            node = nodes_list[n]
            next_node = nodes_list[n+1]

            # Gets the max speed of the way
            max_speed = tags.get('maxspeed_mph')
            if not max_speed:
                max_speed = DEFAULT_SPEED_LIMIT_MPH[tags['highway']]

            # Calculates cost values
            dist = great_circle_distance(node_coords[node], node_coords[next_node])
            time = dist / max_speed

            # Fills cost_map and node_map in the forwards direction
            cost_map[(node, next_node)] = (dist, time)
            node_map.setdefault(node, []).append(next_node)
            node_map.setdefault(next_node, [])

            if twoway: # Also fills the maps in the reverse direction
                cost_map[(next_node, node)] = (dist, time)
                node_map[next_node].append(node)

    return (node_map, node_coords, cost_map)


def find_short_path_nodes(map_rep, node1, node2, heuristic=None, use_time=False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep (tuple): internal representation containing node_map,
            node_coords, cost_map
        node1 (int): node ID representing the start location
        node2 (int): node ID representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    expanded_nodes = set()

    # Agenda contains (cost, path) tuples
    # Paths are tuples of node IDs
    agenda = [(0, (node1,))]

    node_map, node_coords, cost_map = map_rep

    while agenda:
        if heuristic:
            agenda.sort(key=lambda p: p[0]+heuristic(p[1][-1]))
        else:
            agenda.sort() # Sorts on item 0 in tuple, which is the cost
        min_path = agenda.pop(0)

        total_cost, path_nodes = min_path
        terminal_vertex = path_nodes[-1] # Grabs the last node in the path

        if terminal_vertex in expanded_nodes:
            continue

        if terminal_vertex == node2:
            return min_path[1] # Returns the path of node IDs

        expanded_nodes.add(terminal_vertex)
        children = node_map[terminal_vertex] # Gets the neighboring node IDs

        for child_node in children:
            if child_node not in expanded_nodes:
                # Gets the path cost from cost_map
                if use_time: # Calculate using time
                    extra_cost = cost_map[(terminal_vertex, child_node)][1]
                else: # Calculate using dist
                    extra_cost = cost_map[(terminal_vertex, child_node)][0]
                child_path = path_nodes + (child_node,)
                # Adds new (cost, path) tuple to the agenda
                agenda.append((total_cost + extra_cost, child_path))

def get_closest_node(node_coords, loc):
    """
    Returns the node ID of the closest node to a given latitude and longitude

    Parameters:
        node_coords (dict) : a reference of all node IDs and corresponding locs
            * key (int) : a node ID
            * value (tuple) : a tuple containing the corresponding latitude
                and longitude as (lat, lon)
        loc (tuple) : the desired coordinates as (lat, lon)

    Returns:
        closest_node_id (int) : the ID of the closest node to loc
    """
    closest_node_id = 0
    closest_node_dist = 540

    # Checks the distance of each node in the list of nodes from the loc
    # and picks the smallest
    for node in node_coords:
        dist = great_circle_distance(node_coords[node], loc)
        if dist < closest_node_dist:
            closest_node_id = node
            closest_node_dist = dist

    return closest_node_id

def remaining_dist(node_coords, goal_coords):
    """
    Returns a function that calculates the distance from a given node to
    the target for use as a heuristic
    """
    def great_circle_left(node):
        return great_circle_distance(node_coords[node], goal_coords)
    return great_circle_left

def find_short_path(map_rep, loc1, loc2, use_heuristic=False):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """

    node_map = map_rep[0]
    node_coords = map_rep[1]

    n1 = get_closest_node(node_coords, loc1)
    n2 = get_closest_node(node_coords, loc2)

    if use_heuristic:
        heuristic = remaining_dist(node_coords, loc2)
        shortest_path_nodes = find_short_path_nodes(map_rep, n1, n2, heuristic)
    else:
        shortest_path_nodes = find_short_path_nodes(map_rep, n1, n2)

    # Converts nodes in path to coord tuples using node_coords lookup
    path_coords = []
    if shortest_path_nodes:
        for node in shortest_path_nodes:
            path_coords.append(node_coords[node])

    if path_coords:
        return path_coords


def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """

    node_coords = map_rep[1]

    node1 = get_closest_node(node_coords, loc1)
    node2 = get_closest_node(node_coords, loc2)

    # Uses short_path_nodes with time cost instead of dist_cost
    fastest_path_nodes = find_short_path_nodes(map_rep, node1, node2, use_time=True)

    # Converts nodes in path to coord tuples using node_coords lookup
    path_coords = []
    if fastest_path_nodes:
        for node in fastest_path_nodes:
            path_coords.append(node_coords[node])

    if path_coords:
        return path_coords

def BFS(map_rep, node1, node2):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep (tuple): internal representation containing node_map,
            node_coords, cost_map
        node1 (int): node ID representing the start location
        node2 (int): node ID representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    visited_nodes = set()

    # Agenda contains (cost, path) tuples
    # Paths are tuples of node IDs
    agenda = [(node1,)]

    node_map, node_coords, cost_map = map_rep

    while agenda:
        path = agenda.pop(0)
        terminal_vertex = path[-1] # Grabs the last node in the path

        children = node_map[terminal_vertex] # Gets the neighboring node IDs

        for child_node in children:
            child_path = path + (child_node,)
            if child_node == node2:
                return child_path
            if child_node not in visited_nodes:
                agenda.append(child_path)
                visited_nodes.add(terminal_vertex)


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    map_rep = build_internal_representation('resources/midwest.nodes', 'resources/midwest.ways')

    # w/o heuristic: 420555 paths pulled
    # w/ heuristic: 52186 paths

    # print(find_short_path_nodes(map_rep, 2, 8))
    # print(find_short_path(map_rep, (42.3575, -71.0956), (42.3575, -71.0940)))
    # print(find_short_path(map_rep, (42.3858, -71.0783), (42.5465, -71.1787)))
    # print(find_short_path(map_rep, (42.3858, -71.0783), (42.5465, -71.1787), use_heuristic=True))
    print(len(find_short_path_nodes(map_rep, 272855431, 233945564)))
    print(len(BFS(map_rep, 272855431, 233945564)))
