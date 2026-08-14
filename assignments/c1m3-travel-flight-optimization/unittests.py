import numpy as np
from dlai_grader.grading import test_case
from types import FunctionType
from typing import Any, Callable, List, Tuple, Union
from dlai_grader.io import suppress_stdout_stderr
import time
import random

def print_feedback(test_cases: List[test_case]) -> None:
    """Prints feedback of public unit tests within notebook.

    Args:
        test_cases (List[test_case]): List of public test cases.
    """
    failed_cases = [t for t in test_cases if t.failed]
    feedback_msg = "\033[92m All tests passed!\n  If you made your solution in a different cell, make sure to include it in the graded cell as well."

    if failed_cases:
        feedback_msg = ""
        for failed_case in failed_cases:
            feedback_msg += f"\033[91mFailed test case: {failed_case.msg}.\nExpected: {failed_case.want}\nGot: {failed_case.got}\n\n"

    print(feedback_msg)


def generate_graph_json(num_nodes, num_edges_per_node=None, complete=False,
                        weight_bounds=(1, 100), directed=False, seed=None):
    """
    Generates a graph in JSON format with specified parameters.

    Parameters:
    - num_nodes (int): The number of nodes in the graph.
    - num_edges_per_node (int, optional): Target number of edges per node for sparse graphs.
      Ignored if complete=True.
    - complete (bool): If True, creates a complete graph (edge between every pair of nodes).
    - weight_bounds (tuple): (min, max) for random edge weights.
    - directed (bool): If True, creates a directed graph.
    - seed (int, optional): Random seed for reproducibility.

    Returns:
    - dict: Graph in JSON format with 'nodes', 'edges', and 'directed' fields.
    """
    if seed is not None:
        random.seed(seed)

    # Create nodes (numbered 0 to num_nodes-1)
    nodes = list(range(num_nodes))
    edges = []

    if complete:
        # Create edge between every pair of nodes
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                weight = random.randint(weight_bounds[0], weight_bounds[1])
                edges.append({"from": i, "to": j, "weight": weight})
                if directed:
                    weight_back = random.randint(weight_bounds[0], weight_bounds[1])
                    edges.append({"from": j, "to": i, "weight": weight_back})
    else:
        # Create sparse graph with approximately num_edges_per_node edges per node
        if num_edges_per_node is None:
            num_edges_per_node = min(3, num_nodes - 1)

        edge_set = set()
        for i in range(num_nodes):
            edges_added = 0
            attempts = 0
            max_attempts = num_nodes * 2

            while edges_added < num_edges_per_node and attempts < max_attempts:
                j = random.randint(0, num_nodes - 1)
                if i != j:
                    edge_key = (min(i, j), max(i, j)) if not directed else (i, j)
                    if edge_key not in edge_set:
                        weight = random.randint(weight_bounds[0], weight_bounds[1])
                        edges.append({"from": i, "to": j, "weight": weight})
                        edge_set.add(edge_key)
                        edges_added += 1
                attempts += 1

    return {
        "nodes": nodes,
        "edges": edges,
        "directed": directed
    }


def calculate_path_weight(graph_json, path):
    """
    Calculate the total weight of a path in a graph.

    Parameters:
    - graph_json (dict): Graph in JSON format
    - path (list): List of nodes representing a path

    Returns:
    - int/float: Total weight of the path, or None if path is invalid
    """
    if not path or len(path) < 2:
        return 0

    # Build adjacency dict for quick lookup
    adjacency = {}
    for node in graph_json['nodes']:
        adjacency[node] = {}

    is_directed = graph_json.get('directed', False)

    for edge in graph_json['edges']:
        adjacency[edge['from']][edge['to']] = edge['weight']
        if not is_directed:
            adjacency[edge['to']][edge['from']] = edge['weight']

    # Calculate path weight
    total_weight = 0
    for i in range(len(path) - 1):
        if path[i] not in adjacency or path[i+1] not in adjacency[path[i]]:
            return None  # Invalid path
        total_weight += adjacency[path[i]][path[i+1]]

    return total_weight


def is_valid_path(graph_json, path, start_node, end_node):
    """
    Verify that a path is valid and connects start to end.

    Parameters:
    - graph_json (dict): Graph in JSON format
    - path (list): List of nodes representing a path
    - start_node: Expected starting node
    - end_node: Expected ending node

    Returns:
    - bool: True if path is valid, False otherwise
    """
    # Empty path is only valid if no path exists
    if not path:
        return not path_exists(graph_json, start_node, end_node)

    # Check start and end
    if path[0] != start_node or path[-1] != end_node:
        return False

    # Check all edges exist
    weight = calculate_path_weight(graph_json, path)
    return weight is not None


def path_exists(graph_json, start_node, end_node):
    """
    Check if any path exists between start and end using BFS.

    Parameters:
    - graph_json (dict): Graph in JSON format
    - start_node: Starting node
    - end_node: Ending node

    Returns:
    - bool: True if path exists, False otherwise
    """
    if start_node == end_node:
        return True

    # Build adjacency list
    adjacency = {}
    for node in graph_json['nodes']:
        adjacency[node] = []

    is_directed = graph_json.get('directed', False)

    for edge in graph_json['edges']:
        adjacency[edge['from']].append(edge['to'])
        if not is_directed:
            adjacency[edge['to']].append(edge['from'])

    if start_node not in adjacency or end_node not in adjacency:
        return False

    # BFS
    from collections import deque
    queue = deque([start_node])
    visited = {start_node}

    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor == end_node:
                return True
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False


def find_optimal_path_weight(graph_json, start_node, end_node):
    """
    Find the optimal (shortest) path weight using Dijkstra's algorithm.
    Used to verify student solution is optimal.

    Parameters:
    - graph_json (dict): Graph in JSON format
    - start_node: Starting node
    - end_node: Ending node

    Returns:
    - int/float: Optimal path weight, or None if no path exists
    """
    import heapq

    # Build adjacency list
    adjacency = {}
    for node in graph_json['nodes']:
        adjacency[node] = {}

    is_directed = graph_json.get('directed', False)

    for edge in graph_json['edges']:
        adjacency[edge['from']][edge['to']] = edge['weight']
        if not is_directed:
            adjacency[edge['to']][edge['from']] = edge['weight']

    if start_node not in adjacency or end_node not in adjacency:
        return None

    if start_node == end_node:
        return 0

    # Dijkstra's algorithm
    distances = {node: float('inf') for node in graph_json['nodes']}
    distances[start_node] = 0
    pq = [(0, start_node)]
    visited = set()

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == end_node:
            return current_dist

        for neighbor, weight in adjacency[current_node].items():
            if neighbor not in visited:
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))

    return None


def test_find_shortest_path(student_function):
    """
    Test the student's find_shortest_path function.

    Parameters:
    - student_function: The student's implementation of find_shortest_path
    """
    def g():
        function_name = "find_shortest_path"
        cases = []

        # Check if function is callable
        t = test_case()
        if not callable(student_function):
            t.failed = True
            t.msg = f"find_shortest_path must be a function"
            t.want = "A callable function named find_shortest_path"
            t.got = f"Got type {type(student_function).__name__}"
            return [t]

        # Define test graphs
        # Graph 1: Sparse graph with 100 nodes
        graph1 = generate_graph_json(
            num_nodes=100,
            num_edges_per_node=5,
            complete=False,
            weight_bounds=(1, 50),
            directed=False,
            seed=42
        )

        # Graph 2: Sparse graph with 200 nodes
        graph2 = generate_graph_json(
            num_nodes=200,
            num_edges_per_node=4,
            complete=False,
            weight_bounds=(1, 100),
            directed=False,
            seed=123
        )

        # Graph 3: Sparse graph with 150 nodes (directed)
        graph3 = generate_graph_json(
            num_nodes=150,
            num_edges_per_node=6,
            complete=False,
            weight_bounds=(5, 75),
            directed=True,
            seed=999
        )

        # Test cases: (graph, start_node, end_node, expected_weight)
        # Optimal weights computed using compute_test_solutions.py
        test_cases = [
            # Graph 1 tests
            (graph1, 0, 50, 23),
            (graph1, 10, 90, 29),

            # Graph 2 tests
            (graph2, 0, 100, 79),
            (graph2, 25, 175, 47),

            # Graph 3 tests (directed)
            (graph3, 0, 75, 74),
            (graph3, 20, 140, 101),
        ]

        random.seed(42)

        # Run tests
        for i, (graph, start, end, expected_weight) in enumerate(test_cases):
            t = test_case()

            # Determine graph parameters for error messages
            if graph == graph1:
                graph_params = "generate_graph_json(num_nodes=100, num_edges_per_node=5, seed=42)"
            elif graph == graph2:
                graph_params = "generate_graph_json(num_nodes=200, num_edges_per_node=4, seed=123)"
            else:
                graph_params = "generate_graph_json(num_nodes=150, num_edges_per_node=6, directed=True, seed=999)"

            try:
                # Call student function
                result = student_function(graph, start, end)

                # Check if result is a list
                if not isinstance(result, list):
                    t.failed = True
                    t.msg = f"Test {i+1}: find_shortest_path must return a list. Path from {start} to {end}. To replicate: {graph_params}"
                    t.want = "A list of nodes"
                    t.got = f"Type {type(result).__name__}"
                    cases.append(t)
                    continue

                # Check if path is valid
                if not is_valid_path(graph, result, start, end):
                    t.failed = True
                    t.msg = f"Test {i+1}: Invalid path returned for path from {start} to {end}. To replicate: {graph_params}"
                    t.want = f"Valid path from {start} to {end}"
                    t.got = f"Invalid path: {result}"
                    cases.append(t)
                    continue

                # If expected_weight is None (placeholder), compute it
                if expected_weight is None:
                    expected_weight = find_optimal_path_weight(graph, start, end)

                # Check if path weight is optimal
                if result:  # Non-empty path
                    path_weight = calculate_path_weight(graph, result)

                    if expected_weight is None:
                        # No path should exist
                        if result != []:
                            t.failed = True
                            t.msg = f"Test {i+1}: No path exists from {start} to {end}, but got non-empty result. To replicate: {graph_params}"
                            t.want = "Empty list []"
                            t.got = f"{result}"
                    elif path_weight != expected_weight:
                        t.failed = True
                        t.msg = f"Test {i+1}: Path from {start} to {end} is not optimal. To replicate: {graph_params}"
                        t.want = f"Path with weight {expected_weight}"
                        t.got = f"Path with weight {path_weight}"
                else:
                    # Empty path returned - check if correct
                    if expected_weight is not None:
                        t.failed = True
                        t.msg = f"Test {i+1}: Path exists from {start} to {end}, but got empty list. To replicate: {graph_params}"
                        t.want = f"Path with weight {expected_weight}"
                        t.got = "Empty list []"

            except Exception as e:
                t.failed = True
                t.msg = f"Test {i+1}: Exception raised for path from {start} to {end}. To replicate: {graph_params}"
                t.want = "Function to execute without errors"
                t.got = f"Exception: {str(e)}"

            cases.append(t)

        return cases

    cases = g()
    print_feedback(cases)


def calculate_tour_distance(graph_json, tour):
    """
    Calculate the total distance of a TSP tour.

    Parameters:
    - graph_json (dict): Graph in JSON format
    - tour (list): List of nodes in tour order (closed tour: starts and ends with same node)

    Returns:
    - int/float: Total distance of the closed tour
    """
    if not tour or len(tour) < 2:
        return float('inf')

    # Build adjacency dict
    adjacency = {}
    for node in graph_json['nodes']:
        adjacency[node] = {}

    for edge in graph_json['edges']:
        adjacency[edge['from']][edge['to']] = edge['weight']
        if not graph_json.get('directed', False):
            adjacency[edge['to']][edge['from']] = edge['weight']

    # Calculate tour distance (tour is closed, so iterate through all consecutive pairs)
    total = 0
    for i in range(len(tour) - 1):
        from_node = tour[i]
        to_node = tour[i + 1]

        if from_node not in adjacency or to_node not in adjacency[from_node]:
            return float('inf')  # Invalid tour

        total += adjacency[from_node][to_node]

    return total


def is_valid_tour(graph_json, tour, start_node):
    """
    Validate that a tour is valid for TSP.

    Parameters:
    - graph_json (dict): Graph in JSON format
    - tour (list): Proposed tour (closed: starts and ends with same node)
    - start_node: Expected starting node

    Returns:
    - tuple: (is_valid, error_message)
    """
    if not isinstance(tour, list):
        return False, f"Tour must be a list, got {type(tour).__name__}"

    if not tour:
        return False, "Tour is empty"

    if tour[0] != start_node:
        return False, f"Tour must start with {start_node}, got {tour[0]}"

    # Check that tour is closed (returns to start)
    if tour[-1] != start_node:
        return False, f"Tour must end with {start_node} (closed tour), got {tour[-1]}"

    # Check all nodes are in graph
    graph_nodes = set(graph_json['nodes'])
    for node in tour:
        if node not in graph_nodes:
            return False, f"Node {node} not in graph"

    # Check all graph nodes are in tour (excluding the closing node)
    tour_nodes = set(tour[:-1])  # Exclude the closing node
    if tour_nodes != graph_nodes:
        missing = graph_nodes - tour_nodes
        extra = tour_nodes - graph_nodes
        if missing:
            return False, f"Tour missing nodes: {missing}"
        if extra:
            return False, f"Tour has extra nodes: {extra}"

    # Check no duplicates (excluding the closing node)
    if len(tour[:-1]) != len(tour_nodes):
        return False, "Tour has duplicate nodes (excluding closing node)"

    return True, ""


def load_world_tour_graph_for_tests(csv_file='data/world_tour_countries.csv'):
    """
    Load world tour country distances from CSV for testing.

    Parameters:
    - csv_file (str): Path to CSV file

    Returns:
    - dict: Graph in JSON format, or None if file not found
    """
    import csv

    nodes = set()
    edges = []
    country_info = {}

    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                from_node = int(row['from'])
                to_node = int(row['to'])
                distance = int(row['distance_km'])

                nodes.add(from_node)
                nodes.add(to_node)

                if from_node not in country_info:
                    country_info[from_node] = {
                        'name': row['from_name'],
                        'code': row['from_code']
                    }
                if to_node not in country_info:
                    country_info[to_node] = {
                        'name': row['to_name'],
                        'code': row['to_code']
                    }

                edges.append({
                    'from': from_node,
                    'to': to_node,
                    'weight': distance
                })
    except FileNotFoundError:
        return None, None

    graph_json = {
        'nodes': sorted(list(nodes)),
        'edges': edges,
        'directed': False
    }

    return graph_json, country_info


def find_optimal_tsp_brute_force(graph_json, start_node):
    """
    Find the optimal TSP tour using brute force (for small graphs only).

    Parameters:
    - graph_json (dict): Complete graph in JSON format
    - start_node: Starting node

    Returns:
    - tuple: (optimal_tour, optimal_distance) where tour is closed [start, ..., start]
    """
    from itertools import permutations

    nodes = graph_json['nodes']
    if len(nodes) > 10:
        raise ValueError("Brute force only works for ≤10 nodes")

    # Build adjacency matrix
    adjacency = {}
    for node in nodes:
        adjacency[node] = {}

    for edge in graph_json['edges']:
        adjacency[edge['from']][edge['to']] = edge['weight']
        if not graph_json.get('directed', False):
            adjacency[edge['to']][edge['from']] = edge['weight']

    # Get other nodes (excluding start)
    other_nodes = [n for n in nodes if n != start_node]

    best_tour = None
    best_distance = float('inf')

    # Try all permutations
    for perm in permutations(other_nodes):
        tour = [start_node] + list(perm) + [start_node]  # Closed tour

        # Calculate distance
        distance = 0
        valid = True
        for i in range(len(tour) - 1):
            from_node = tour[i]
            to_node = tour[i + 1]
            if to_node not in adjacency[from_node]:
                valid = False
                break
            distance += adjacency[from_node][to_node]

        if valid and distance < best_distance:
            best_distance = distance
            best_tour = tour

    return best_tour, best_distance


def test_optimize_world_tour(student_function, solution_function=None):
    """
    Test the student's optimize_world_tour function.

    Parameters:
    - student_function: The function to test
    - solution_function: Optional reference solution to use for comparison.
                        If provided, this function will be used as the baseline for the
                        30% threshold. If not provided, uses an embedded
                        Nearest Neighbor reference implementation.

                        Usage example:
                        # Test student against your own solution
                        test_optimize_world_tour(student_function, solution_function=my_solution)

                        # Test student against embedded reference
                        test_optimize_world_tour(student_function)

    Tests solutions against Nearest Neighbor heuristic:
    - All graphs: Must find solution within 30% of reference Nearest Neighbor solution
    """
    def g():
        function_name = "optimize_world_tour"
        cases = []

        # Check if function is callable
        t = test_case()
        if not callable(student_function):
            t.failed = True
            t.msg = f"{function_name} must be a function"
            t.want = "A callable function named optimize_world_tour"
            t.got = f"Got type {type(student_function).__name__}"
            return [t]

        # Load the full world tour graph
        full_graph, country_info = load_world_tour_graph_for_tests()

        if full_graph is None:
            t = test_case()
            t.failed = True
            t.msg = "Could not load world_tour_countries.csv"
            t.want = "world_tour_countries.csv file in data/ directory"
            t.got = "File not found"
            return [t]

        # =====================================================================
        # Setup reference solution (Nearest Neighbor)
        # =====================================================================

        # Determine which reference solution to use
        if solution_function is not None:
            # Use provided solution function as reference
            reference_solution = solution_function
        else:
            # Use embedded reference solution (Nearest Neighbor only)
            def reference_solution(graph_json, start_node):
                """Reference implementation using Nearest Neighbor"""
                nodes = graph_json['nodes']
                adjacency = {n: {} for n in nodes}

                for edge in graph_json['edges']:
                    adjacency[edge['from']][edge['to']] = edge['weight']
                    if not graph_json.get('directed', False):
                        adjacency[edge['to']][edge['from']] = edge['weight']

                # Nearest Neighbor
                tour = [start_node]
                unvisited = set(nodes) - {start_node}
                current = start_node

                while unvisited:
                    nearest = min(unvisited, key=lambda n: adjacency[current].get(n, float('inf')))
                    tour.append(nearest)
                    unvisited.remove(nearest)
                    current = nearest

                # Close the tour
                tour.append(start_node)
                return tour

        # =====================================================================
        # Test with various graph sizes
        # =====================================================================
        all_nodes = sorted(full_graph['nodes'])

        test_configs = []

        # Small graphs (5-8 nodes)
        if len(all_nodes) >= 5:
            test_configs.append((all_nodes[:5], all_nodes[0], "5 countries"))
        if len(all_nodes) >= 8:
            test_configs.append((all_nodes[:8], all_nodes[0], "8 countries"))

        # Medium graphs (10-15 nodes)
        if len(all_nodes) >= 10:
            test_configs.append((all_nodes[:10], all_nodes[0], "10 countries"))
        if len(all_nodes) >= 12:
            test_configs.append((all_nodes[:12], all_nodes[0], "12 countries"))
        if len(all_nodes) >= 15:
            test_configs.append((all_nodes[:15], all_nodes[0], "15 countries"))

        # Large graphs (20+ nodes)
        if len(all_nodes) >= 20:
            test_configs.append((all_nodes[:20], all_nodes[0], "20 countries"))
        if len(all_nodes) >= 45:
            test_configs.append((all_nodes[:45], all_nodes[0], "45 countries"))
        if len(all_nodes) >= 80:
            test_configs.append((all_nodes[:80], all_nodes[0], "80 countries"))

        for test_idx, (subset_nodes, start_node, description) in enumerate(test_configs):
            t = test_case()

            try:
                # Create subgraph
                subgraph_edges = []
                for edge in full_graph['edges']:
                    if edge['from'] in subset_nodes and edge['to'] in subset_nodes:
                        subgraph_edges.append(edge)

                subgraph = {
                    'nodes': subset_nodes,
                    'edges': subgraph_edges,
                    'directed': False
                }

                # Get reference solution distance
                reference_tour = reference_solution(subgraph, start_node)
                reference_distance = calculate_tour_distance(subgraph, reference_tour)

                # 30% threshold (relaxed from 25% to allow for randomness in tie-breaking)
                max_acceptable_distance = reference_distance * 1.30

                # Call student function
                result = student_function(subgraph, start_node)

                # Validate result
                if not isinstance(result, list):
                    t.failed = True
                    t.msg = f"Test {test_idx+1}: Must return a list ({description})"
                    t.want = "A list of node numbers"
                    t.got = f"Type {type(result).__name__}"
                    cases.append(t)
                    continue

                is_valid, error_msg = is_valid_tour(subgraph, result, start_node)
                if not is_valid:
                    t.failed = True
                    t.msg = f"Test {test_idx+1}: Invalid tour ({description}). {error_msg}"
                    t.want = f"Valid tour visiting all {len(subset_nodes)} nodes"
                    t.got = f"Invalid tour: {result}"
                    cases.append(t)
                    continue

                # Calculate student's tour distance
                student_distance = calculate_tour_distance(subgraph, result)

                # Check if within 30% of reference
                if student_distance > max_acceptable_distance:
                    t.failed = True
                    percent_over = ((student_distance / reference_distance) - 1) * 100
                    t.msg = f"Test {test_idx+1}: Solution not within acceptable range ({description})"
                    t.want = f"Tour distance ≤ {max_acceptable_distance:.0f} (within 30% of reference: {reference_distance:.0f})"
                    t.got = f"Tour distance: {student_distance:.0f} ({percent_over:.1f}% over reference)"
                    cases.append(t)
                    continue

                # Test passed - show quality
                percent_diff = ((student_distance / reference_distance) - 1) * 100
                if student_distance < reference_distance:
                    quality = f"✨ Better than reference! ({-percent_diff:.1f}% improvement)"
                elif abs(percent_diff) < 1:
                    quality = f"🌟 Excellent! (matches reference)"
                elif percent_diff < 10:
                    quality = f"✓ Good! (within {percent_diff:.1f}% of reference)"
                else:
                    quality = f"✓ Acceptable (within {percent_diff:.1f}% of reference)"

                t.msg = f"Test {test_idx+1}: {quality} ({description}): {student_distance:.0f}"
                cases.append(t)

            except Exception as e:
                t.failed = True
                t.msg = f"Test {test_idx+1}: Exception ({description})"
                t.want = "Function to execute without errors"
                t.got = f"Exception: {str(e)}"
                cases.append(t)

        return cases

    cases = g()
    print_feedback(cases)


def test_tsp_large_graph(student_function):
    """Placeholder for TSP large graph tests"""
    print("TSP Large Graph tests not yet implemented for new format")


def test_tsp_medium_graph(student_function):
    """Placeholder for TSP medium graph tests"""
    print("TSP Medium Graph tests not yet implemented for new format")
