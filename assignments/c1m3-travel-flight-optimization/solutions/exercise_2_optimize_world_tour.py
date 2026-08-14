# GRADED CELL 2 - Do NOT delete this cell or rename the function.
# You can add helper functions within this cell.
def optimize_world_tour(graph_json, start_node):
    """
    Find a tour visiting all countries using the Nearest Neighbor algorithm.

    Parameters:
    - graph_json (dict): Graph in JSON format with country nodes
    - start_node (int): The node to start and end the tour

    Returns:
    - list: Ordered list of node numbers representing the tour (including return to start)
            Example: [0, 3, 5, 2, 1, 0] - starts and ends with the same node
    """
    ### START CODE HERE ###
    nodes = graph_json.get("nodes", [])
    edges = graph_json.get("edges", [])
    directed = graph_json.get("directed", False)

    adjacency = {node: {} for node in nodes}
    for edge in edges:
        source, target, weight = edge["from"], edge["to"], edge["weight"]
        adjacency[source][target] = weight
        if not directed:
            adjacency[target][source] = weight

    tour = [start_node]
    unvisited = set(nodes) - {start_node}
    current = start_node

    while unvisited:
        nearest = min(
            unvisited,
            key=lambda candidate: adjacency[current].get(candidate, float("inf")),
        )
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest

    tour.append(start_node)
    return tour
    ### END CODE HERE ###
