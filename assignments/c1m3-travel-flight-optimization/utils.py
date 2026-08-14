import plotly.graph_objects as go
import numpy as np
import random
import csv


import csv

def load_continents_graph(csv_file='data/continents_distances.csv'):
    """
    Load continent distances from CSV and convert to graph JSON format.
    
    Continents are mapped to numbered nodes:
    0: North America, 1: South America, 2: Europe, 3: Africa,
    4: Asia, 5: Australia, 6: Antarctica
    
    Parameters:
    - csv_file (str): Path to the CSV file with continent distances
    
    Returns:
    - dict: Graph in JSON format with nodes as integers
    """
    nodes = set()
    edges = []
    node_names = {}
    
    # Read CSV and build graph
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_node = int(row['from'])
            to_node = int(row['to'])
            distance = int(row['distance_km'])
            
            nodes.add(from_node)
            nodes.add(to_node)
            
            # Store node names for reference
            if from_node not in node_names:
                node_names[from_node] = row['from_name']
            if to_node not in node_names:
                node_names[to_node] = row['to_name']
            
            edges.append({
                'from': from_node,
                'to': to_node,
                'weight': distance
            })
    
    graph_json = {
        'nodes': sorted(list(nodes)),
        'edges': edges,
        'directed': False
    }
    
    return graph_json, node_names


# =====================================================================
#  Continent coordinates (centroids)
# =====================================================================
DEFAULT_COORDS = {
    0: {"name": "North America",  "lat": 54.5260,  "lon": -105.2551},
    1: {"name": "South America",  "lat": -8.7832,  "lon": -55.4915},
    2: {"name": "Europe",         "lat": 54.5260,  "lon": 15.2551},
    3: {"name": "Africa",         "lat": 1.6508,   "lon": 17.4439},
    4: {"name": "Asia",           "lat": 34.0479,  "lon": 100.6197},
    5: {"name": "Australia",      "lat": -25.2744, "lon": 133.7751},
    6: {"name": "Antarctica",     "lat": -82.8628, "lon": 135.0000}
}


# =====================================================================
#  Great-circle interpolation
# =====================================================================
def great_circle(lon1, lat1, lon2, lat2, n_points=200):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    t = np.linspace(0, 1, n_points)

    x1, y1, z1 = np.cos(lat1)*np.cos(lon1), np.cos(lat1)*np.sin(lon1), np.sin(lat1)
    x2, y2, z2 = np.cos(lat2)*np.cos(lon2), np.cos(lat2)*np.sin(lon2), np.sin(lat2)

    omega = np.arccos(np.clip(x1*x2 + y1*y2 + z1*z2, -1, 1))
    sin_omega = np.sin(omega)

    xyz = (np.sin((1-t)*omega)/sin_omega)[:, None] * np.array([x1, y1, z1]) + \
          (np.sin(t*omega)/sin_omega)[:, None] * np.array([x2, y2, z2])

    lats = np.degrees(np.arctan2(xyz[:, 2], np.sqrt(xyz[:, 0] ** 2 + xyz[:, 1] ** 2)))
    lons = np.degrees(np.arctan2(xyz[:, 1], xyz[:, 0]))

    return lons, lats


# =====================================================================
#  Arrowhead (polyline-based — stable)
# =====================================================================
def arrow_polyline(lons, lats, size_deg=3.0):
    """
    Create arrowhead using two visible polylines (left→tip, right→tip).
    Avoids projection distortion issues.
    """
    lonC, latC = lons[-1], lats[-1]      # arrow tip
    lonB, latB = lons[-4], lats[-4]      # earlier point for direction

    angle = np.arctan2(latC - latB, lonC - lonB)

    # Wings at ±135°
    left_angle  = angle + 3 * np.pi / 4
    right_angle = angle - 3 * np.pi / 4

    left_lon  = lonC + size_deg * np.cos(left_angle)
    left_lat  = latC + size_deg * np.sin(left_angle)

    right_lon = lonC + size_deg * np.cos(right_angle)
    right_lat = latC + size_deg * np.sin(right_angle)

    return [
        ([left_lon, lonC],  [left_lat,  latC]),
        ([right_lon, lonC], [right_lat, latC])
    ]


# =====================================================================
#  Main plotting function
# =====================================================================
def plot_continent_path(path, coords=None, title="Continent Path", scope="world"):
    """
    Plot a path of continent indices on a world map with great-circle arcs
    and visible arrowheads.

    - path: list of continent node IDs (e.g., [1, 5, 2, 6])
    - coords: dictionary of node → {name, lat, lon}
    - scope: map scope - "world", "north america", "south america", or custom bounds
    """

    if coords is None:
        coords = DEFAULT_COORDS

    fig = go.Figure()

    # ------------------------------------------------------------
    # Plot continent markers
    # ------------------------------------------------------------
    for idx, c in coords.items():
        # Build hover text with all information
        hover_text = c["name"]
        if "capital" in c:
            hover_text = f"<b>{c['name']}</b><br>Capital: {c['capital']}"

        # Add position info
        position_info = ""
        if idx == path[0]:
            position_info = "<br>🏁 START"
        elif idx == path[-1]:
            position_info = "<br>🏁 END"
        else:
            # Find position in path
            if idx in path:
                pos = path.index(idx) + 1
                position_info = f"<br>Stop #{pos}"

        hover_text += position_info

        # Determine marker styling based on position in path
        if idx == path[0]:
            # Starting point - pastel emerald
            marker_color = "#6EE7B7"
            marker_size = 10
            marker_symbol = "circle"
        elif idx == path[-1]:
            # End point - pastel coral
            marker_color = "#FCA5A5"
            marker_size = 10
            marker_symbol = "circle"
        else:
            # Intermediate points - pastel amber/gold
            marker_color = "#FCD34D"
            marker_size = 8
            marker_symbol = "circle"

        fig.add_trace(go.Scattergeo(
            lon=[c["lon"]],
            lat=[c["lat"]],
            mode="markers",  # Only markers, no text
            hovertext=hover_text,
            hoverinfo="text",
            marker=dict(
                size=marker_size,
                color=marker_color,
                symbol=marker_symbol,
                line=dict(width=1, color="white")
            ),
            showlegend=False
        ))

    # We store the arrowheads so we can render them on top
    arrow_traces = []

    # ------------------------------------------------------------
    # Plot path arcs + build arrowheads
    # ------------------------------------------------------------
    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]

        lon1, lat1 = coords[a]["lon"], coords[a]["lat"]
        lon2, lat2 = coords[b]["lon"], coords[b]["lat"]

        # Great-circle line
        lons, lats = great_circle(lon1, lat1, lon2, lat2)

        # Main curve - soft pastel travel route style
        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="lines",
            line=dict(
                width=1.5,
                color="#5EEAD4",  # Pastel teal/turquoise
                dash="solid"
            ),
            opacity=0.65,
            showlegend=False
        ))

        # Arrowhead - deeper teal for visibility
        for ah_lon, ah_lat in arrow_polyline(lons, lats, size_deg=1.5):
            arrow_traces.append(go.Scattergeo(
                lon=ah_lon,
                lat=ah_lat,
                mode="lines",
                line=dict(
                    width=2,
                    color="#2DD4BF"  # Deeper teal for arrows
                ),
                showlegend=False
            ))

    # ------------------------------------------------------------
    # Add arrowheads LAST (so they appear on top)
    # ------------------------------------------------------------
    for tr in arrow_traces:
        fig.add_trace(tr)

    # ------------------------------------------------------------
    # Map styling - Professional cartographic style
    # ------------------------------------------------------------
    # Configure geo settings based on scope - Soft pastel palette
    geo_config = {
        "showcountries": True,
        "showland": True,
        "landcolor": "#FAF8F5",           # Very light warm cream for land
        "oceancolor": "#EFF6FF",          # Very light pastel blue for ocean
        "showocean": True,
        "coastlinecolor": "#D1D5DB",      # Light gray for coastlines
        "coastlinewidth": 0.8,
        "countrycolor": "#E5E7EB",        # Very light gray for country borders
        "countrywidth": 0.6,
        "showlakes": True,
        "lakecolor": "#F0F9FF",           # Even lighter pastel blue for lakes
        "bgcolor": "#FEFEFE"              # Almost white background
    }

    # Handle different scope options
    if scope == "world":
        geo_config["scope"] = "world"
        geo_config["projection_type"] = "natural earth"
    elif scope in ["north america", "south america"]:
        # Plotly built-in scopes
        geo_config["scope"] = scope
        geo_config["projection_type"] = "albers usa" if scope == "north america" else "mercator"
    elif scope == "americas":
        # Custom bounds for all Americas (North + Central + South + Caribbean)
        geo_config["projection_type"] = "mercator"
        geo_config["lataxis"] = {"range": [-60, 70]}
        geo_config["lonaxis"] = {"range": [-170, -30]}
    else:
        # Default to world if scope not recognized
        geo_config["scope"] = "world"
        geo_config["projection_type"] = "natural earth"

    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 20,
                'color': '#1F2937',
                'family': 'Arial, sans-serif',
                'weight': 'bold'
            }
        },
        geo=geo_config,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#374151"
        ),
        showlegend=False,
        height=700
    )

    fig.show()


def plot_graph_with_path(graph_json, nodes_path):
    """
    Plot a graph and highlight a path formed by connected nodes with directional arrows.
    Uses NetworkX and Matplotlib for visualization with edge weights as actual distances.

    Parameters:
    - graph_json (dict): Graph in JSON format with 'nodes', 'edges', and optional 'directed'
    - nodes_path (list): List of nodes forming a path (assumes nodes are connected)

    Example:
    >>> graph = generate_graph_json(5, complete=True, seed=42)
    >>> plot_graph_with_path(graph, [0, 3, 4, 1])
    """
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Installing required libraries...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "networkx", "matplotlib"])
        import networkx as nx
        import matplotlib.pyplot as plt
        import numpy as np

    # Create NetworkX graph from JSON structure
    if graph_json.get('directed', False):
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    # Add nodes
    G.add_nodes_from(graph_json['nodes'])

    # Add edges with weights
    for edge in graph_json['edges']:
        G.add_edge(edge['from'], edge['to'], weight=edge['weight'])

    # Build path edges set for highlighting
    path_edges_set = set()
    if nodes_path and len(nodes_path) > 1:
        for i in range(len(nodes_path) - 1):
            if graph_json.get('directed', False):
                path_edges_set.add((nodes_path[i], nodes_path[i+1]))
            else:
                # For undirected, normalize the edge representation
                edge_tuple = tuple(sorted([nodes_path[i], nodes_path[i+1]]))
                path_edges_set.add(edge_tuple)

    # Calculate positions based on actual edge weights
    nodes = list(G.nodes())
    n = len(nodes)
    
    # Initialize positions randomly
    np.random.seed(42)
    pos = {node: np.random.rand(2) * 10 for node in nodes}
    
    # Get edge weights
    edges_with_weights = []
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        edges_with_weights.append((u, v, weight))
    
    # Normalize weights to reasonable visual scale
    weights = [w for _, _, w in edges_with_weights]
    min_weight = min(weights)
    max_weight = max(weights)
    weight_range = max_weight - min_weight if max_weight > min_weight else 1
    
    # Scale factor to convert weights to visual distances
    # Map weight range to visual distance range (e.g., 1 to 5 units)
    scale_factor = 5.0 / weight_range if weight_range > 0 else 1.0
    
    # Force-directed layout that respects edge weights as distances
    # Use iterative spring-mass system
    iterations = 1000
    learning_rate = 0.01
    
    for iteration in range(iterations):
        forces = {node: np.array([0.0, 0.0]) for node in nodes}
        
        # Spring forces: edges want to be at their ideal length (weight)
        for u, v, weight in edges_with_weights:
            pos_u = pos[u]
            pos_v = pos[v]
            
            # Vector from u to v
            delta = pos_v - pos_u
            current_dist = np.linalg.norm(delta)
            
            if current_dist < 0.01:
                current_dist = 0.01
                
            # Ideal distance is proportional to edge weight
            ideal_dist = weight * scale_factor
            
            # Spring force proportional to displacement from ideal length
            force_magnitude = (current_dist - ideal_dist) * 0.5
            force_direction = delta / current_dist
            force = force_magnitude * force_direction
            
            # Apply forces
            forces[u] += force
            forces[v] -= force
        
        # Repulsive forces between all node pairs (to prevent overlap)
        repulsion_strength = 5.0
        for i, node_i in enumerate(nodes):
            for node_j in nodes[i+1:]:
                pos_i = pos[node_i]
                pos_j = pos[node_j]
                
                delta = pos_j - pos_i
                dist = np.linalg.norm(delta)
                
                if dist < 0.1:
                    dist = 0.1
                
                # Repulsive force inversely proportional to distance
                force_magnitude = repulsion_strength / (dist * dist)
                force_direction = delta / dist
                force = force_magnitude * force_direction
                
                forces[node_i] -= force
                forces[node_j] += force
        
        # Update positions
        for node in nodes:
            pos[node] = pos[node] + learning_rate * forces[node]
        
        # Reduce learning rate over time
        learning_rate *= 0.995
    
    # Convert positions to numpy arrays
    pos = {node: np.array(position) for node, position in pos.items()}

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))

    # Separate edges into path and non-path
    regular_edges = []
    path_edges = []

    for edge in G.edges():
        u, v = edge
        if graph_json.get('directed', False):
            is_path_edge = (u, v) in path_edges_set
        else:
            is_path_edge = tuple(sorted([u, v])) in path_edges_set

        if is_path_edge:
            path_edges.append(edge)
        else:
            regular_edges.append(edge)

    # Draw regular edges (gray, thin)
    nx.draw_networkx_edges(
        G, pos,
        edgelist=regular_edges,
        width=1.5,
        alpha=0.4,
        edge_color='#D1D5DB',
        ax=ax,
        arrows=graph_json.get('directed', False),
        arrowsize=15
    )

    # Draw path edges (red, thick)
    nx.draw_networkx_edges(
        G, pos,
        edgelist=path_edges,
        width=4,
        alpha=0.9,
        edge_color='#DC2626',
        ax=ax,
        arrows=True,
        arrowsize=20,
        arrowstyle='->'
    )

    # Determine node colors based on path
    node_colors = []
    node_sizes = []

    for node in G.nodes():
        if nodes_path and node in nodes_path:
            if node == nodes_path[0]:
                node_colors.append('#34D399')  # Green for start
                node_sizes.append(1200)
            elif node == nodes_path[-1]:
                node_colors.append('#F87171')  # Red for end
                node_sizes.append(1200)
            else:
                node_colors.append('#FBBF24')  # Amber for path
                node_sizes.append(1000)
        else:
            node_colors.append('#E5E7EB')  # Gray for others
            node_sizes.append(800)

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors='white',
        linewidths=2,
        ax=ax
    )

    # Draw node labels
    nx.draw_networkx_labels(
        G, pos,
        font_size=12,
        font_weight='bold',
        font_color='#111827',
        ax=ax
    )

    # Draw edge weight labels
    for edge in G.edges():
        u, v = edge
        weight = G[u][v]['weight']

        if graph_json.get('directed', False):
            is_path_edge = (u, v) in path_edges_set
        else:
            is_path_edge = tuple(sorted([u, v])) in path_edges_set

        # Calculate midpoint
        x = (pos[u][0] + pos[v][0]) / 2
        y = (pos[u][1] + pos[v][1]) / 2

        # Draw label
        ax.text(
            x, y, str(weight),
            fontsize=10 if is_path_edge else 8,
            color='#DC2626' if is_path_edge else '#9CA3AF',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'),
            ha='center',
            va='center'
        )

    # Set title
    if nodes_path:
        path_str = ' → '.join(map(str, nodes_path))
        ax.set_title(f'Graph with Path: {path_str}', fontsize=16, fontweight='bold', pad=20)
    else:
        ax.set_title('Graph Visualization', fontsize=16, fontweight='bold', pad=20)

    # Equal aspect ratio and remove axes
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()
    plt.show()

    # Print path details
    if nodes_path and len(nodes_path) > 1:
        edge_weights_dict = {}
        for edge in graph_json['edges']:
            edge_weights_dict[(edge['from'], edge['to'])] = edge['weight']
            if not graph_json.get('directed', False):
                edge_weights_dict[(edge['to'], edge['from'])] = edge['weight']

        total_weight = 0
        print(f"\n📍 Path Details:")
        print("=" * 55)
        for i in range(len(nodes_path) - 1):
            from_node = nodes_path[i]
            to_node = nodes_path[i + 1]
            weight = edge_weights_dict.get((from_node, to_node), 0)
            total_weight += weight
            print(f"  Step {i+1:2d}: Node {from_node} → Node {to_node}  (weight: {weight:6.1f})")
        print("=" * 55)
        print(f"  Total Path Weight: {total_weight:.1f}")
        print(f"  Nodes Visited: {len(nodes_path)}")
        print(f"  Edges Traversed: {len(nodes_path) - 1}\n")


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

"""
Graph JSON Validation Function

This function checks if a given dictionary follows the required JSON graph structure.
"""


def validate_graph_json(graph_json, verbose=True):
    """
    Validate that a graph follows the required JSON structure for this assignment.

    Required structure:
    {
        "nodes": [list of hashable node identifiers],
        "edges": [
            {"from": node, "to": node, "weight": positive_number},
            ...
        ],
        "directed": boolean (optional, defaults to False)
    }

    Parameters:
    - graph_json: The graph dictionary to validate
    - verbose (bool): If True, prints detailed error messages

    Returns:
    - tuple: (is_valid, error_messages)
        - is_valid (bool): True if graph is valid, False otherwise
        - error_messages (list): List of error messages (empty if valid)

    Example:
    >>> graph = {
    ...     "nodes": [0, 1, 2],
    ...     "edges": [{"from": 0, "to": 1, "weight": 5}]
    ... }
    >>> is_valid, errors = validate_graph_json(graph)
    >>> print(is_valid)
    True
    """
    errors = []

    # Check if graph_json is a dictionary
    if not isinstance(graph_json, dict):
        errors.append(f"Graph must be a dictionary, got {type(graph_json).__name__}")
        if verbose:
            for error in errors:
                print(f"❌ {error}")
        return False, errors

    # Check for required 'nodes' field
    if 'nodes' not in graph_json:
        errors.append("Missing required field 'nodes'")
    elif not isinstance(graph_json['nodes'], list):
        errors.append(f"Field 'nodes' must be a list, got {type(graph_json['nodes']).__name__}")
    else:
        # Check that all nodes are hashable
        for i, node in enumerate(graph_json['nodes']):
            try:
                hash(node)
            except TypeError:
                errors.append(f"Node at index {i} ({node}) is not hashable")

        # Check for duplicate nodes
        if len(graph_json['nodes']) != len(set(graph_json['nodes'])):
            errors.append("Duplicate nodes found in 'nodes' list")

    # Check for required 'edges' field
    if 'edges' not in graph_json:
        errors.append("Missing required field 'edges'")
    elif not isinstance(graph_json['edges'], list):
        errors.append(f"Field 'edges' must be a list, got {type(graph_json['edges']).__name__}")
    else:
        # Validate each edge
        for i, edge in enumerate(graph_json['edges']):
            if not isinstance(edge, dict):
                errors.append(f"Edge at index {i} must be a dictionary, got {type(edge).__name__}")
                continue

            # Check for required edge fields
            if 'from' not in edge:
                errors.append(f"Edge at index {i} missing required field 'from'")
            elif 'nodes' in graph_json and edge['from'] not in graph_json['nodes']:
                errors.append(f"Edge at index {i}: 'from' node {edge['from']} not in nodes list")

            if 'to' not in edge:
                errors.append(f"Edge at index {i} missing required field 'to'")
            elif 'nodes' in graph_json and edge['to'] not in graph_json['nodes']:
                errors.append(f"Edge at index {i}: 'to' node {edge['to']} not in nodes list")

            if 'weight' not in edge:
                errors.append(f"Edge at index {i} missing required field 'weight'")
            elif not isinstance(edge['weight'], (int, float)):
                errors.append(f"Edge at index {i}: 'weight' must be a number, got {type(edge['weight']).__name__}")
            elif edge['weight'] <= 0:
                errors.append(f"Edge at index {i}: 'weight' must be positive, got {edge['weight']}")

    # Check optional 'directed' field
    if 'directed' in graph_json:
        if not isinstance(graph_json['directed'], bool):
            errors.append(f"Field 'directed' must be a boolean, got {type(graph_json['directed']).__name__}")

    # Check for unexpected fields (warning, not error)
    expected_fields = {'nodes', 'edges', 'directed'}
    unexpected_fields = set(graph_json.keys()) - expected_fields
    if unexpected_fields and verbose:
        print(f"⚠️  Warning: Unexpected fields found: {unexpected_fields}")

    # Print results
    if verbose:
        if errors:
            print(f"\n❌ Graph validation failed with {len(errors)} error(s):")
            for error in errors:
                print(f"   • {error}")
        else:
            print("✅ Graph structure is valid!")
            print(f"   • {len(graph_json.get('nodes', []))} nodes")
            print(f"   • {len(graph_json.get('edges', []))} edges")
            print(f"   • {'Directed' if graph_json.get('directed', False) else 'Undirected'} graph")

    return len(errors) == 0, errors


# =====================================================================
#  Exercise 3: World Tour Helper Functions
# =====================================================================

def load_world_tour_graph(csv_file='data/all_americas_countries.csv'):
    """
    Load world tour country distances from CSV.

    Parameters:
    - csv_file (str): Path to the CSV file with country distances
                     Default: 'data/all_americas_countries.csv' (35 countries)
                     Use 'data/world_tour_countries.csv' for 15-country subset

    Returns:
    - graph_json: Graph in JSON format with country nodes
    - country_info: Dictionary mapping node IDs to country information
    """
    nodes = set()
    edges = []
    country_info = {}

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

    graph_json = {
        'nodes': sorted(list(nodes)),
        'edges': edges,
        'directed': False
    }

    return graph_json, country_info


def load_flight_network(countries_csv='data/world_countries_by_continent.csv',
                        flights_csv='data/world_flights.csv'):
    """
    Load realistic flight network (sparse graph) for shortest path finding.

    This network represents actual flight routes between countries, where not all
    country pairs have direct flights. Perfect for testing shortest path algorithms.

    Parameters:
    - countries_csv (str): Path to countries/continent mapping CSV
    - flights_csv (str): Path to flight routes CSV

    Returns:
    - graph_json: Graph in JSON format (sparse, ~16% density)
    - country_info: Dictionary mapping node IDs to country info
    - continents: Dictionary mapping continent names to lists of country node IDs
    - flight_info: Dictionary with flight statistics
    """
    # Load country information
    country_info = {}
    continents = {}

    with open(countries_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = int(row['node_id'])
            continent = row['continent']

            country_info[node_id] = {
                'name': row['country_name'],
                'code': row['country_code'],
                'continent': continent,
                'lat': float(row['lat']),
                'lon': float(row['lon'])
            }

            if continent not in continents:
                continents[continent] = []
            continents[continent].append(node_id)

    # Load flight routes
    edges = []
    price_stats = {'min': float('inf'), 'max': 0, 'total': 0}

    with open(flights_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            price = float(row['price_usd'])
            edges.append({
                'from': int(row['from']),
                'to': int(row['to']),
                'weight': price,  # Use price as weight for shortest path
                'distance_km': int(row['distance_km']),
                'price_usd': price
            })

            price_stats['min'] = min(price_stats['min'], price)
            price_stats['max'] = max(price_stats['max'], price)
            price_stats['total'] += price

    graph_json = {
        'nodes': sorted(list(country_info.keys())),
        'edges': edges,
        'directed': False
    }

    flight_info = {
        'total_routes': len(edges),
        'total_countries': len(country_info),
        'avg_price': price_stats['total'] / len(edges) if edges else 0,
        'min_price': price_stats['min'],
        'max_price': price_stats['max'],
        'density': len(edges) / (len(country_info) * (len(country_info) - 1) / 2) if len(country_info) > 1 else 0
    }

    return graph_json, country_info, continents, flight_info


def load_world_graph_with_continents(countries_csv='data/world_countries_by_continent.csv',
                                      distances_csv='data/world_distances.csv'):
    """
    Load world graph with continent information.

    Parameters:
    - countries_csv (str): Path to countries/continent mapping CSV
    - distances_csv (str): Path to distance matrix CSV

    Returns:
    - graph_json: Graph in JSON format
    - country_info: Dictionary mapping node IDs to country info (name, code, continent, lat, lon)
    - continents: Dictionary mapping continent names to lists of country node IDs
    """
    # Load country information with continents
    country_info = {}
    continents = {}

    with open(countries_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            node_id = int(row['node_id'])
            continent = row['continent']

            country_info[node_id] = {
                'name': row['country_name'],
                'code': row['country_code'],
                'continent': continent,
                'lat': float(row['lat']),
                'lon': float(row['lon'])
            }

            # Group by continent
            if continent not in continents:
                continents[continent] = []
            continents[continent].append(node_id)

    # Load distances
    edges = []
    with open(distances_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges.append({
                'from': int(row['from']),
                'to': int(row['to']),
                'weight': int(row['distance_km'])
            })

    graph_json = {
        'nodes': sorted(list(country_info.keys())),
        'edges': edges,
        'directed': False
    }

    return graph_json, country_info, continents


def calculate_tour_distance(graph_json, tour):
    """
    Calculate the total distance of a closed tour.

    Parameters:
    - graph_json (dict): Graph in JSON format
    - tour (list): List of nodes in tour order (closed tour: starts and ends with same node)

    Returns:
    - float: Total tour distance in kilometers
    """
    # Build adjacency matrix
    adjacency = {n: {} for n in graph_json['nodes']}
    for edge in graph_json['edges']:
        adjacency[edge['from']][edge['to']] = edge['weight']
        if not graph_json.get('directed', False):
            adjacency[edge['to']][edge['from']] = edge['weight']

    # Calculate total distance (tour is closed, iterate through consecutive pairs)
    total = 0
    for i in range(len(tour) - 1):
        from_node = tour[i]
        to_node = tour[i + 1]
        total += adjacency[from_node][to_node]

    return total


def create_country_coords_for_plot():
    """
    Create coordinate mapping for all 35 Americas countries using capital cities.

    Returns:
    - dict: Mapping of node IDs to country information with capital city lat/lon coordinates
    """
    coords = {
        # North America (3)
        0:  {"name": "Canada", "capital": "Ottawa", "lat": 45.4215, "lon": -75.6972, "code": "CA"},
        1:  {"name": "United States", "capital": "Washington D.C.", "lat": 38.9072, "lon": -77.0369, "code": "US"},
        2:  {"name": "Mexico", "capital": "Mexico City", "lat": 19.4326, "lon": -99.1332, "code": "MX"},
        # Central America (7)
        3:  {"name": "Belize", "capital": "Belmopan", "lat": 17.2510, "lon": -88.7590, "code": "BZ"},
        4:  {"name": "Guatemala", "capital": "Guatemala City", "lat": 14.6349, "lon": -90.5069, "code": "GT"},
        5:  {"name": "Honduras", "capital": "Tegucigalpa", "lat": 14.0650, "lon": -87.1715, "code": "HN"},
        6:  {"name": "El Salvador", "capital": "San Salvador", "lat": 13.6929, "lon": -89.2182, "code": "SV"},
        7:  {"name": "Nicaragua", "capital": "Managua", "lat": 12.1150, "lon": -86.2362, "code": "NI"},
        8:  {"name": "Costa Rica", "capital": "San José", "lat": 9.9281, "lon": -84.0907, "code": "CR"},
        9:  {"name": "Panama", "capital": "Panama City", "lat": 8.9824, "lon": -79.5199, "code": "PA"},
        # Caribbean (13)
        10: {"name": "Cuba", "capital": "Havana", "lat": 23.1136, "lon": -82.3666, "code": "CU"},
        11: {"name": "Jamaica", "capital": "Kingston", "lat": 17.9714, "lon": -76.7931, "code": "JM"},
        12: {"name": "Haiti", "capital": "Port-au-Prince", "lat": 18.5944, "lon": -72.3074, "code": "HT"},
        13: {"name": "Dominican Republic", "capital": "Santo Domingo", "lat": 18.4861, "lon": -69.9312, "code": "DO"},
        14: {"name": "Puerto Rico", "capital": "San Juan", "lat": 18.4655, "lon": -66.1057, "code": "PR"},
        15: {"name": "Trinidad and Tobago", "capital": "Port of Spain", "lat": 10.6918, "lon": -61.2225, "code": "TT"},
        16: {"name": "Barbados", "capital": "Bridgetown", "lat": 13.0969, "lon": -59.6145, "code": "BB"},
        17: {"name": "The Bahamas", "capital": "Nassau", "lat": 25.0343, "lon": -77.3963, "code": "BS"},
        18: {"name": "Grenada", "capital": "St. George's", "lat": 12.0561, "lon": -61.7488, "code": "GD"},
        19: {"name": "Saint Lucia", "capital": "Castries", "lat": 14.0101, "lon": -60.9875, "code": "LC"},
        20: {"name": "Saint Vincent", "capital": "Kingstown", "lat": 13.1579, "lon": -61.2248, "code": "VC"},
        21: {"name": "Antigua and Barbuda", "capital": "St. John's", "lat": 17.1274, "lon": -61.8468, "code": "AG"},
        22: {"name": "Dominica", "capital": "Roseau", "lat": 15.3010, "lon": -61.3880, "code": "DM"},
        # South America (12)
        23: {"name": "Colombia", "capital": "Bogotá", "lat": 4.7110, "lon": -74.0721, "code": "CO"},
        24: {"name": "Venezuela", "capital": "Caracas", "lat": 10.4806, "lon": -66.9036, "code": "VE"},
        25: {"name": "Guyana", "capital": "Georgetown", "lat": 6.8013, "lon": -58.1551, "code": "GY"},
        26: {"name": "Suriname", "capital": "Paramaribo", "lat": 5.8520, "lon": -55.2038, "code": "SR"},
        27: {"name": "Brazil", "capital": "Brasília", "lat": -15.8267, "lon": -47.9218, "code": "BR"},
        28: {"name": "Ecuador", "capital": "Quito", "lat": -0.1807, "lon": -78.4678, "code": "EC"},
        29: {"name": "Peru", "capital": "Lima", "lat": -12.0464, "lon": -77.0428, "code": "PE"},
        30: {"name": "Bolivia", "capital": "La Paz", "lat": -16.5000, "lon": -68.1500, "code": "BO"},
        31: {"name": "Chile", "capital": "Santiago", "lat": -33.4489, "lon": -70.6693, "code": "CL"},
        32: {"name": "Argentina", "capital": "Buenos Aires", "lat": -34.6037, "lon": -58.3816, "code": "AR"},
        33: {"name": "Paraguay", "capital": "Asunción", "lat": -25.2637, "lon": -57.5759, "code": "PY"},
        34: {"name": "Uruguay", "capital": "Montevideo", "lat": -34.9011, "lon": -56.1645, "code": "UY"},
    }
    return coords


def create_americas_tour_widget(optimize_world_tour):
    """
    Create an interactive widget for building custom tours across the Americas.

    This widget allows users to:
    - Select any combination of countries from 35 Americas countries
    - Compute the shortest tour using their optimize_world_tour implementation
    - Visualize the tour on an interactive map
    - See the tour route and total distance

    Parameters:
    - optimize_world_tour: The user's implementation of the optimize_world_tour function

    Returns:
    - None (displays the widget)
    """
    import ipywidgets as widgets
    from IPython.display import display, clear_output
    import plotly.graph_objects as go

    # Load ALL Americas countries data (35 countries)
    all_americas_graph, all_country_info = load_world_tour_graph('data/all_americas_countries.csv')
    coords = create_country_coords_for_plot()

    # Organize countries by region for easier selection
    regions = {
        'North America': [0, 1, 2],  # Canada, USA, Mexico
        'Central America': [3, 4, 5, 6, 7, 8, 9],  # Belize to Panama
        'Caribbean': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        'South America': [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
    }

    # Create checkboxes organized by region
    checkboxes = {}
    region_widgets = []

    for region_name, country_ids in regions.items():
        region_label = widgets.HTML(f"<b>{region_name}:</b>")
        region_boxes = []

        for node_id in country_ids:
            if node_id in all_country_info:
                info = all_country_info[node_id]
                cb = widgets.Checkbox(
                    value=(node_id < 15),  # First 15 selected
                    description=info['name'][:20],
                    layout=widgets.Layout(width='180px'),
                    indent=False
                )
                checkboxes[node_id] = cb
                region_boxes.append(cb)

        region_widgets.append(region_label)
        region_widgets.extend(region_boxes)

    # Left panel with scrollable area
    left_scroll = widgets.VBox(
        region_widgets,
        layout=widgets.Layout(height='400px', overflow_y='auto', width='200px')
    )

    # Buttons
    compute_button = widgets.Button(
        description='Compute Shortest Tour',
        button_style='success',
        icon='route',
        layout=widgets.Layout(width='200px', height='40px')
    )

    select_all_button = widgets.Button(
        description='Select All',
        button_style='info',
        layout=widgets.Layout(width='95px', height='30px')
    )

    clear_all_button = widgets.Button(
        description='Clear All',
        button_style='warning',
        layout=widgets.Layout(width='95px', height='30px')
    )

    button_row = widgets.HBox([select_all_button, clear_all_button])

    left_panel = widgets.VBox([
        widgets.HTML("<h4 style='margin:5px 0'>Select Countries:</h4>"),
        left_scroll,
        button_row,
        compute_button
    ], layout=widgets.Layout(padding='10px'))

    # Map output
    map_output = widgets.Output(layout=widgets.Layout(width='600px', height='500px'))

    # Display initial map
    with map_output:
        # Create map with all country markers
        fig = go.Figure()

        for node_id in sorted(coords.keys()):
            c = coords[node_id]
            fig.add_trace(go.Scattergeo(
                lon=[c["lon"]],
                lat=[c["lat"]],
                mode="markers",
                marker=dict(size=8, color="#3B82F6", line=dict(width=1, color="white")),
                hovertext=f"<b>{c['name']}</b>",
                hoverinfo="text",
                showlegend=False
            ))

        fig.update_geos(
            showcountries=True,
            showland=True,
            landcolor="#FAF8F5",
            oceancolor="#EFF6FF",
            showocean=True,
            coastlinecolor="#D1D5DB",
            coastlinewidth=0.8,
            countrycolor="#E5E7EB",
            scope="south america",
            projection_type="mercator",
            center=dict(lon=-75, lat=0),
            lataxis_range=[-60, 60],
            lonaxis_range=[-120, -30]
        )

        fig.update_layout(
            title="Select countries and click Compute Tour",
            height=500,
            margin=dict(l=0, r=0, t=40, b=0)
        )

        fig.show()

    # Right panel - results
    results_output = widgets.Output(layout=widgets.Layout(
        width='200px',
        height='500px',
        border='1px solid #ddd',
        padding='10px'
    ))

    with results_output:
        selected_count = sum(1 for cb in checkboxes.values() if cb.value)
        print(f"{selected_count} countries")
        print("selected")
        print()
        print("Select countries")
        print("from the list")
        print()
        print("Then click")
        print("'Compute Tour'")

    right_panel = widgets.VBox([
        widgets.HTML("<h4 style='margin:5px 0'>Status:</h4>"),
        results_output
    ])

    def on_compute_tour(b):
        """Compute and display the tour"""

        # Get selected countries
        selected = [node_id for node_id, cb in checkboxes.items() if cb.value]

        if len(selected) < 2:
            with results_output:
                clear_output()
                print("⚠️ Error")
                print()
                print("Select at least")
                print("2 countries")
            return

        # Show computing
        with results_output:
            clear_output()
            print("Computing the")
            print("shortest tour...")

        # Create subgraph
        selected_set = set(selected)
        subgraph_edges = []

        for edge in all_americas_graph['edges']:
            if edge['from'] in selected_set and edge['to'] in selected_set:
                subgraph_edges.append(edge)

        subgraph = {
            'nodes': sorted(selected),
            'edges': subgraph_edges,
            'directed': False
        }

        # Compute tour
        try:
            start_node = min(selected)
            tour = optimize_world_tour(subgraph, start_node)

            if not tour:
                with results_output:
                    clear_output()
                    print("Error:")
                    print("No tour found")
                return

            distance = calculate_tour_distance(subgraph, tour)

            # Update map
            with map_output:
                clear_output(wait=True)
                filtered_coords = {k: v for k, v in coords.items() if k in selected_set}
                plot_continent_path(tour, coords=filtered_coords,
                                  title=f"Tour: {distance:,} km",
                                  scope="americas")

            # Show results
            with results_output:
                clear_output()
                print("✅ Shortest path")
                print("found!")
                print()
                print(f"Length:")
                print(f"{distance:,} km")
                print()
                print("Tour:")
                for i, node_id in enumerate(tour, 1):
                    name = all_country_info[node_id]['name']
                    if len(name) > 15:
                        name = name[:12] + "..."
                    print(f"{i}. {name}")

        except Exception as e:
            with results_output:
                clear_output()
                print("Error computing")
                print("tour")

    def on_select_all(b):
        """Select all countries"""
        for cb in checkboxes.values():
            cb.value = True
        with results_output:
            clear_output()
            print(f"{len(checkboxes)} countries")
            print("selected")

    def on_clear_all(b):
        """Clear all selections"""
        for cb in checkboxes.values():
            cb.value = False
        with results_output:
            clear_output()
            print("0 countries")
            print("selected")

    # Attach handlers
    compute_button.on_click(on_compute_tour)
    select_all_button.on_click(on_select_all)
    clear_all_button.on_click(on_clear_all)

    # Main layout
    main_widget = widgets.HBox([
        left_panel,
        map_output,
        right_panel
    ])

    print("\n🌎 Interactive Americas Tour Builder\n")
    display(main_widget)


def launch_tour_widget(optimize_world_tour, find_shortest_path, port=5000):
    """
    Launch an improved interactive tour widget in a separate browser window.

    This opens a Flask server with dual-mode functionality:
    1. Shortest Path Mode - Find cheapest flight route between two countries
    2. TSP Tour Mode - Find optimal tour visiting multiple countries

    Parameters:
    - optimize_world_tour: The student's TSP optimization function
    - find_shortest_path: The student's shortest path function
    - port (int): Port number for the Flask server (default: 5000)

    Usage:
        from utils import launch_tour_widget
        launch_tour_widget(optimize_world_tour, find_shortest_path)

    The widget provides:
    - Dual-mode operation (shortest path + TSP tour)
    - Realistic flight network (106 routes, 16% density)
    - Flight price-based routing
    - Continental filtering
    - Interactive map visualization
    - Real-time cost calculations

    To stop the server: Press Ctrl+C in the Jupyter notebook cell
    """
    import sys
    import os

    # Import and run the Flask server
    widget_server_path = os.path.join(os.path.dirname(__file__), 'tour_widget_server.py')

    if not os.path.exists(widget_server_path):
        print("❌ Error: tour_widget_server.py not found")
        print(f"   Expected location: {widget_server_path}")
        return

    # Import the server module
    import importlib.util
    spec = importlib.util.spec_from_file_location("tour_widget_server", widget_server_path)
    server_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_module)

    # Launch the widget with both functions
    server_module.launch_widget(optimize_world_tour, find_shortest_path, port=port)