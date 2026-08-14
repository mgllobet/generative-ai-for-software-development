# GRADED CELL 1 - Do NOT delete this cell or rename the function.
# You can add helper functions within this cell.
def find_shortest_path(graph_json, start_node, end_node):
    """
    Find the shortest path between start_node and end_node in the graph.

    Parameters:
    - graph_json (dict): Graph in JSON format with 'nodes', 'edges', and optional 'directed' fields
    - start_node: The starting node (must be in graph_json['nodes'])
    - end_node: The ending node (must be in graph_json['nodes'])

    Returns:
    - list: A list of nodes representing the shortest path from start_node to end_node,
            including both start_node and end_node.
            Returns an empty list [] if no path exists.
    """
    ### START CODE HERE ###
    import heapq

    nodes = graph_json.get("nodes", [])
    edges = graph_json.get("edges", [])
    directed = graph_json.get("directed", False)

    if start_node not in nodes or end_node not in nodes:
        return []
    if start_node == end_node:
        return [start_node]

    adjacency = {node: [] for node in nodes}
    for edge in edges:
        source, target, weight = edge["from"], edge["to"], edge["weight"]
        adjacency[source].append((target, weight))
        if not directed:
            adjacency[target].append((source, weight))

    distances = {node: float("inf") for node in nodes}
    distances[start_node] = 0
    predecessors = {start_node: None}
    priority_queue = [(0, start_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end_node:
            break
        if current_distance > distances[current_node]:
            continue

        for neighbor, edge_weight in adjacency[current_node]:
            candidate_distance = current_distance + edge_weight
            if candidate_distance < distances[neighbor]:
                distances[neighbor] = candidate_distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (candidate_distance, neighbor))

    if distances[end_node] == float("inf"):
        return []

    path = []
    node = end_node
    while node is not None:
        path.append(node)
        node = predecessors.get(node)
    path.reverse()
    return path
    ### END CODE HERE ###
