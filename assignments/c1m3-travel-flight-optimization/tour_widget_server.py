"""
================================================================================
WORLD TOUR WIDGET SERVER - Interactive Flask Application
================================================================================

OVERVIEW:
This server provides a web interface for graph algorithms with two modes:
1. SHORTEST PATH MODE - Find cheapest flight routes between countries
2. TSP TOUR MODE - Find optimal tour visiting multiple countries

ARCHITECTURE:
- Flask web server with REST API endpoints
- Plotly for interactive map visualizations
- Dual-mode functionality (shortest path + TSP)

FOR LEARNERS:
This file is designed to be easily modified. Each section is clearly marked
and documented. Common modifications are explained in comments.

USAGE:
From Jupyter notebook:
    from utils import launch_tour_widget
    launch_tour_widget(optimize_world_tour, find_shortest_path)

================================================================================
"""

# ============================================================================
# SECTION 1: IMPORTS
# ============================================================================
# Standard library imports
import json
import threading
import webbrowser

# Third-party imports
from flask import Flask, render_template, jsonify, request
import plotly.graph_objects as go

# Local imports
from utils import load_flight_network


# ============================================================================
# SECTION 2: APPLICATION SETUP
# ============================================================================

app = Flask(__name__)

# Global state - stores user functions and data
widget_state = {
    'optimize_function': None,        # User's TSP optimization function
    'shortest_path_function': None,   # User's shortest path function
    'flight_graph': None,             # Flight network (sparse graph with prices)
    'country_info': None,             # Country metadata (name, coordinates, etc.)
    'continents': None,               # Continent groupings
    'flight_info': None               # Flight network statistics
}


# ============================================================================
# SECTION 3: WEB PAGE ROUTES
# ============================================================================

@app.route('/')
def index():
    """
    Serve the main widget HTML page.

    MODIFICATION TIP:
    - To use a different template, change 'tour_widget.html' to your filename
    - Template must be in the 'templates/' folder
    """
    return render_template('tour_widget.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Serve static files (CSS, JavaScript, images).

    This allows the widget to load widget_config.js from the static/ folder.

    MODIFICATION TIP:
    - Add custom CSS files to static/ folder
    - Add custom JavaScript files to static/ folder
    - Files will be accessible at /static/filename
    """
    from flask import send_from_directory
    import os
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_folder, filename)


# ============================================================================
# SECTION 4: DATA API ENDPOINTS
# ============================================================================

@app.route('/api/continents')
def get_continents():
    """
    API endpoint: Get all continents and their countries.

    RETURNS:
        JSON with continents list and flight statistics

    MODIFICATION TIP:
    - To add country filters, modify the 'countries' list comprehension
    - To add more metadata, update the country info dictionary
    """
    if widget_state['continents'] is None:
        return jsonify({'error': 'Widget not initialized'}), 500

    continents_data = []

    for continent_name in sorted(widget_state['continents'].keys()):
        country_ids = widget_state['continents'][continent_name]

        # Build country list for this continent
        countries = []
        for node_id in sorted(country_ids):
            info = widget_state['country_info'][node_id]
            countries.append({
                'id': node_id,
                'name': info['name'],
                'code': info['code']
            })

        continents_data.append({
            'name': continent_name,
            'countries': countries,
            'count': len(countries)
        })

    return jsonify({
        'continents': continents_data,
        'flight_stats': widget_state['flight_info']
    })


# ============================================================================
# SECTION 5: SHORTEST PATH API
# ============================================================================

@app.route('/api/shortest_path', methods=['POST'])
def find_shortest_path_endpoint():
    """
    API endpoint: Find k-shortest paths between two countries.

    REQUEST BODY:
        {
            "start_node": int,    # Starting country ID
            "end_node": int,      # Destination country ID
            "k": int (optional)   # Number of alternative routes (default: 4)
        }

    RETURNS:
        JSON with multiple route options sorted by cost

    MODIFICATION TIP:
    - To change number of routes, modify default 'k' value
    - To use different routing algorithm, update the call to shortest_path_function
    - To filter routes by criteria, add filtering after all_routes is populated
    """
    # Parse request
    data = request.json
    start_node = data.get('start_node')
    end_node = data.get('end_node')
    k = data.get('k', 4)  # Default: find 4 alternative routes

    # Validate input
    if start_node is None or end_node is None:
        return jsonify({'error': 'Please select both start and end countries'}), 400

    if start_node == end_node:
        return jsonify({'error': 'Start and end must be different countries'}), 400

    try:
        # Find multiple alternative paths
        all_routes = find_k_shortest_paths(start_node, end_node, k)

        if len(all_routes) == 0:
            return jsonify({'error': 'No path found between these countries'}), 404

        # Sort routes by cost (already sorted, but ensure)
        all_routes.sort(key=lambda r: r['total_cost'])

        return jsonify({
            'routes': all_routes,
            'num_routes_found': len(all_routes)
        })

    except Exception as e:
        return jsonify({'error': f'Error finding path: {str(e)}'}), 500


# ============================================================================
# SECTION 6: TSP TOUR API
# ============================================================================

@app.route('/api/compute_tour', methods=['POST'])
def compute_tour_endpoint():
    """
    API endpoint: Compute optimal TSP tour for selected countries.

    REQUEST BODY:
        {
            "selected_nodes": [int],        # List of country IDs to visit
            "start_node": int,              # Starting country ID
            "optimization_mode": str        # 'distance' or 'cost'
        }

    RETURNS:
        JSON with tour path and statistics

    MODIFICATION TIP:
    - To use different graph representation, modify create_complete_subgraph()
    - To add tour optimization constraints, add checks before calling optimize_function
    - To include more tour statistics, add calculations after tour is computed
    """
    # Parse request
    data = request.json
    selected_nodes = data.get('selected_nodes', [])
    start_node = data.get('start_node', None)
    optimization_mode = data.get('optimization_mode', 'distance')  # Default to distance

    # Validate input
    if len(selected_nodes) < 2:
        return jsonify({'error': 'Please select at least 2 countries'}), 400

    if start_node is None:
        start_node = selected_nodes[0]

    try:
        # Create complete subgraph for TSP based on optimization mode
        if optimization_mode == 'cost':
            filtered_graph = create_complete_subgraph_cost(selected_nodes)
        else:
            filtered_graph = create_complete_subgraph(selected_nodes)

        # Call user's optimization function
        tour = widget_state['optimize_function'](filtered_graph, start_node)

        # Calculate tour statistics
        tour_stats = calculate_tour_statistics(tour, optimization_mode)

        return jsonify(tour_stats)

    except Exception as e:
        return jsonify({'error': f'Error computing tour: {str(e)}'}), 500


# ============================================================================
# SECTION 7: VISUALIZATION API
# ============================================================================

@app.route('/api/initial_map', methods=['GET'])
def get_initial_map():
    """
    API endpoint: Get initial empty world map with all countries marked.

    RETURNS:
        JSON containing Plotly figure with world map and all countries

    MODIFICATION TIP:
    - To customize initial map, modify the visualization parameters
    - To highlight specific regions, add additional traces
    """
    try:
        # Create empty world map with all countries
        fig = go.Figure()

        # Add all country markers
        country_info = widget_state['country_info']
        lats = [info['lat'] for info in country_info.values()]
        lons = [info['lon'] for info in country_info.values()]
        names = [info['name'] for info in country_info.values()]

        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode='markers',
            marker=dict(size=6, color='#667eea', symbol='circle', opacity=0.6),
            hovertext=names,
            hoverinfo='text',
            showlegend=False
        ))

        # Configure map appearance
        fig.update_geos(
            projection_type='natural earth',
            showland=True,
            landcolor='lightgray',
            showocean=True,
            oceancolor='lightblue',
            showcountries=True,
            countrycolor='white',
            bgcolor='rgba(0,0,0,0)'
        )

        # Set title and layout
        fig.update_layout(
            title={
                'text': 'World Flight Network',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#333'}
            },
            height=720,
            margin={'l': 0, 'r': 0, 't': 40, 'b': 0},
            paper_bgcolor='white'
        )

        # Convert to JSON
        plot_json = json.loads(fig.to_json())

        return jsonify({'plot': plot_json})

    except Exception as e:
        return jsonify({'error': f'Error creating initial map: {str(e)}'}), 500


@app.route('/api/plot_path', methods=['POST'])
def plot_path_endpoint():
    """
    API endpoint: Generate Plotly map visualization for a path.

    REQUEST BODY:
        {
            "path": [int],              # List of country IDs in order
            "type": "path" or "tour"    # Path type determines if it loops back
        }

    RETURNS:
        JSON containing Plotly figure

    MODIFICATION TIP:
    - To customize map appearance, modify create_path_map() function
    - To add different map projections, update projection_type parameter
    - To show additional data on map, add more traces in create_path_map()
    """
    # Parse request
    data = request.json
    path = data.get('path', [])
    path_type = data.get('type', 'path')  # 'path' or 'tour'

    # Validate input
    if len(path) < 2:
        return jsonify({'error': 'Path must have at least 2 countries'}), 400

    try:
        # Generate visualization
        fig = create_path_map(path, widget_state['country_info'], path_type)

        # Convert to JSON
        plot_json = json.loads(fig.to_json())

        return jsonify({'plot': plot_json})

    except Exception as e:
        return jsonify({'error': f'Error creating plot: {str(e)}'}), 500


# ============================================================================
# SECTION 8: SHORTEST PATH HELPER FUNCTIONS
# ============================================================================

def find_k_shortest_paths(start_node, end_node, k):
    """
    Find k alternative shortest paths between two nodes.

    ALGORITHM:
    Uses iterative edge removal - finds shortest path, removes most expensive
    edge, finds next shortest path, repeats.

    PARAMETERS:
        start_node: Starting country ID
        end_node: Destination country ID
        k: Number of alternative paths to find

    RETURNS:
        List of route dictionaries, each containing:
            - route_number: Route index (1-based)
            - path: List of node IDs
            - path_info: Detailed country information
            - total_cost: Total flight cost
            - num_countries: Number of countries visited
            - num_flights: Number of flight segments
            - path_details: Detailed segment information

    MODIFICATION TIP:
    - To use Yen's algorithm instead, replace this entire function
    - To prioritize routes differently, change the edge removal strategy
      in create_graph_without_edges()
    """
    all_routes = []

    for route_num in range(k):
        # Determine which graph to use
        if route_num == 0:
            # First iteration: use original graph
            current_graph = widget_state['flight_graph']
        else:
            # Subsequent iterations: exclude edges from previous paths
            current_graph = create_graph_without_edges(
                widget_state['flight_graph'],
                all_routes
            )

        # Call student's shortest path function
        path = widget_state['shortest_path_function'](
            current_graph,
            start_node,
            end_node
        )

        # Check if path was found
        if not path or len(path) == 0:
            break  # No more alternative paths

        # Calculate path cost using original graph prices
        total_cost, path_details = calculate_path_cost(
            path,
            widget_state['flight_graph']
        )

        # Build detailed path information
        path_info = []
        for i, node_id in enumerate(path):
            info = widget_state['country_info'][node_id]
            path_info.append({
                'position': i + 1,
                'id': node_id,
                'name': info['name'],
                'code': info['code'],
                'continent': info['continent']
            })

        # Add route to results
        all_routes.append({
            'route_number': route_num + 1,
            'path': path,
            'path_info': path_info,
            'total_cost': total_cost,
            'num_countries': len(path),
            'num_flights': len(path) - 1,
            'path_details': path_details
        })

    return all_routes


def create_graph_without_edges(original_graph, previous_routes):
    """
    Create graph with specific edges removed to force alternative routes.

    STRATEGY:
    Removes the most expensive edge from each previous route. This tends to
    produce better quality alternative routes.

    PARAMETERS:
        original_graph: Full flight network graph
        previous_routes: List of previously found routes

    RETURNS:
        Modified graph with certain edges removed

    MODIFICATION TIP:
    - To remove different edges, change the selection criteria
    - To remove all edges from previous routes, remove the max_cost logic
    - To use a different edge removal strategy, replace the entire loop
    """
    import copy

    # Create deep copy to avoid modifying original
    new_graph = copy.deepcopy(original_graph)

    # Collect edges to remove
    edges_to_remove = set()

    for route in previous_routes:
        path = route['path']

        if len(path) < 2:
            continue

        # Find the most expensive edge in this path
        max_cost = 0
        max_edge = None

        for i in range(len(path) - 1):
            from_node = path[i]
            to_node = path[i + 1]

            # Find this edge's cost
            for edge in original_graph['edges']:
                if ((edge['from'] == from_node and edge['to'] == to_node) or
                    (edge['from'] == to_node and edge['to'] == from_node)):
                    if edge['price_usd'] > max_cost:
                        max_cost = edge['price_usd']
                        # Store as sorted tuple for undirected graph
                        max_edge = tuple(sorted([from_node, to_node]))
                    break

        if max_edge:
            edges_to_remove.add(max_edge)

    # Filter out the edges to remove
    filtered_edges = []
    for edge in new_graph['edges']:
        edge_key = tuple(sorted([edge['from'], edge['to']]))
        if edge_key not in edges_to_remove:
            filtered_edges.append(edge)

    new_graph['edges'] = filtered_edges

    return new_graph


# ============================================================================
# SECTION 9: TSP HELPER FUNCTIONS
# ============================================================================

def create_complete_subgraph(selected_nodes):
    """
    Create complete graph for selected nodes using distance weights (for TSP).

    TSP requires a complete graph where every node connects to every other
    node. This function filters the global distance matrix to only include
    the selected countries.

    PARAMETERS:
        selected_nodes: List of country IDs to include

    RETURNS:
        Complete graph dictionary with all pairwise connections (distance-based)

    MODIFICATION TIP:
    - To use flight prices instead of distances, change load_world_graph_with_continents
      to load_flight_network and filter flight edges
    - To add edge weights based on custom criteria, modify the edge filtering loop
    """
    from utils import load_world_graph_with_continents

    # Load complete distance matrix
    complete_graph, _, _ = load_world_graph_with_continents()

    # Filter to only include edges between selected nodes
    filtered_edges = []
    for edge in complete_graph['edges']:
        if edge['from'] in selected_nodes and edge['to'] in selected_nodes:
            filtered_edges.append(edge)

    return {
        'nodes': selected_nodes,
        'edges': filtered_edges,
        'directed': False
    }


def create_complete_subgraph_cost(selected_nodes):
    """
    Create complete graph for selected nodes using flight cost weights (for TSP).

    TSP requires a complete graph. Since flight network is sparse (not all countries
    have direct flights), we compute shortest paths between all pairs using the
    user's shortest_path_function.

    PARAMETERS:
        selected_nodes: List of country IDs to include

    RETURNS:
        Complete graph dictionary with all pairwise connections (cost-based)
    """
    # Use the flight graph which has price_usd
    flight_graph = widget_state['flight_graph']

    # Create complete graph by finding shortest path between all pairs
    complete_edges = []

    for i, from_node in enumerate(selected_nodes):
        for to_node in selected_nodes[i+1:]:  # Only upper triangle (undirected)
            # Find shortest path between these two nodes
            path = widget_state['shortest_path_function'](
                flight_graph,
                from_node,
                to_node
            )

            if path and len(path) >= 2:
                # Calculate cost of this path
                cost, _ = calculate_path_cost(path, flight_graph)

                # Add edge with the shortest path cost as weight
                complete_edges.append({
                    'from': from_node,
                    'to': to_node,
                    'weight': cost
                })
            else:
                # No path exists - use a very high cost (effectively infinite)
                # This shouldn't happen if flight network is connected
                complete_edges.append({
                    'from': from_node,
                    'to': to_node,
                    'weight': 999999  # Very high cost
                })

    return {
        'nodes': selected_nodes,
        'edges': complete_edges,
        'directed': False
    }


def calculate_tour_statistics(tour, optimization_mode='distance'):
    """
    Calculate comprehensive statistics for a tour.

    PARAMETERS:
        tour: List of node IDs representing the tour (closed tour: starts and ends with same node)
        optimization_mode: 'distance' or 'cost' - determines which metric to calculate

    RETURNS:
        Dictionary with tour statistics and information

    MODIFICATION TIP:
    - To add more statistics (e.g., longest flight, most expensive segment),
      add calculations in this function
    - To include geographic data (total distance), add distance calculations
    """
    # Build detailed tour information (excluding closing node)
    tour_info = []
    continents_visited = set()

    for i, node_id in enumerate(tour[:-1]):  # Exclude closing node
        info = widget_state['country_info'][node_id]
        tour_info.append({
            'position': i + 1,
            'id': node_id,
            'name': info['name'],
            'code': info['code'],
            'continent': info['continent']
        })
        continents_visited.add(info['continent'])

    # Calculate metrics based on optimization mode
    if optimization_mode == 'cost':
        # Calculate flight cost (tour is already closed)
        total_cost, tour_details = calculate_tour_cost(
            tour,
            widget_state['flight_graph']
        )

        return {
            'tour': tour[:-1],  # Return tour without closing node for display
            'tour_info': tour_info,
            'total_cost': total_cost,
            'num_countries': len(tour) - 1,  # Exclude closing node
            'num_continents': len(continents_visited),
            'continents_visited': sorted(list(continents_visited)),
            'tour_details': tour_details
        }
    else:
        # Calculate distance
        from utils import load_world_graph_with_continents, calculate_tour_distance

        distance_graph, _, _ = load_world_graph_with_continents()
        total_distance = calculate_tour_distance(distance_graph, tour)

        return {
            'tour': tour[:-1],  # Return tour without closing node for display
            'tour_info': tour_info,
            'total_distance': total_distance,
            'num_countries': len(tour) - 1,  # Exclude closing node
            'num_continents': len(continents_visited),
            'continents_visited': sorted(list(continents_visited))
        }


# ============================================================================
# SECTION 10: COST CALCULATION FUNCTIONS
# ============================================================================

def calculate_path_cost(path, graph_json):
    """
    Calculate total cost of a path (one-way, no return).

    PARAMETERS:
        path: List of node IDs in order
        graph_json: Graph containing edge weights

    RETURNS:
        Tuple of (total_cost, path_details)
        - total_cost: Sum of all edge costs
        - path_details: List of segment information

    MODIFICATION TIP:
    - To use distance instead of price, change 'price_usd' to 'distance_km'
    - To add penalties (e.g., per-flight fee), add to total_cost in the loop
    - To calculate average cost per km, divide total by total distance
    """
    # Build adjacency dictionary for fast lookups
    adjacency = {}
    for node in graph_json['nodes']:
        adjacency[node] = {}

    for edge in graph_json['edges']:
        adjacency[edge['from']][edge['to']] = {
            'price': edge['price_usd'],
            'distance': edge['distance_km']
        }
        # Add reverse edge for undirected graphs
        if not graph_json.get('directed', False):
            adjacency[edge['to']][edge['from']] = {
                'price': edge['price_usd'],
                'distance': edge['distance_km']
            }

    # Calculate total cost and collect details
    total_cost = 0
    path_details = []

    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]

        if to_node in adjacency[from_node]:
            flight_info = adjacency[from_node][to_node]
            total_cost += flight_info['price']
            path_details.append({
                'from': from_node,
                'to': to_node,
                'price': flight_info['price'],
                'distance': flight_info['distance']
            })
        else:
            # No direct connection (shouldn't happen for valid paths)
            path_details.append({
                'from': from_node,
                'to': to_node,
                'price': 0,
                'distance': 0,
                'error': 'No direct flight'
            })

    return round(total_cost, 2), path_details


def calculate_tour_cost(tour, graph_json):
    """
    Calculate total cost of a tour (closed tour).

    PARAMETERS:
        tour: List of node IDs (closed tour: starts and ends with same node)
        graph_json: Graph containing edge weights

    RETURNS:
        Tuple of (total_cost, tour_details)

    MODIFICATION TIP:
    - Tour is already closed, so just use calculate_path_cost directly
    - To exclude return cost, use tour[:-1] to remove closing node
    """
    # Tour is already closed, so just calculate the path cost
    return calculate_path_cost(tour, graph_json)


# ============================================================================
# SECTION 11: VISUALIZATION FUNCTIONS
# ============================================================================

def create_path_map(path, country_info, path_type='path'):
    """
    Create interactive Plotly map visualization.

    PARAMETERS:
        path: List of country IDs in visit order
        country_info: Dictionary mapping country IDs to metadata
        path_type: 'path' (one-way) or 'tour' (returns to start)

    RETURNS:
        Plotly Figure object

    MODIFICATION TIP:
    - To change line color/width, modify line=dict() parameters
    - To use different markers, change marker=dict() parameters
    - To add arrows, add arrow traces in the loop
    - To change map projection, modify projection_type
    - To zoom to region, add fitbounds or set lat/lon ranges
    """
    fig = go.Figure()

    # Determine how many segments to draw
    loop_end = len(path) if path_type == 'path' else len(path) + 1

    # Add flight path lines
    for i in range(loop_end - 1):
        from_node = path[i]
        to_node = path[(i + 1) % len(path)] if path_type == 'tour' else path[i + 1]

        from_coord = country_info[from_node]
        to_coord = country_info[to_node]

        # Add line connecting countries
        fig.add_trace(go.Scattergeo(
            lon=[from_coord['lon'], to_coord['lon']],
            lat=[from_coord['lat'], to_coord['lat']],
            mode='lines',
            line=dict(width=2, color='rgba(255, 0, 0, 0.6)'),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Add country markers with position numbers
    path_lats = [country_info[node]['lat'] for node in path]
    path_lons = [country_info[node]['lon'] for node in path]
    path_names = [country_info[node]['name'] for node in path]
    path_positions = [f"#{i+1}" for i in range(len(path))]

    fig.add_trace(go.Scattergeo(
        lon=path_lons,
        lat=path_lats,
        mode='markers+text',
        marker=dict(size=10, color='red', symbol='circle'),
        text=path_positions,
        textposition='top center',
        textfont=dict(size=9, color='darkblue', family='Arial Black'),
        hovertext=path_names,
        hoverinfo='text',
        showlegend=False
    ))

    # Configure map appearance
    fig.update_geos(
        projection_type='natural earth',
        showland=True,
        landcolor='lightgray',
        showocean=True,
        oceancolor='lightblue',
        showcountries=True,
        countrycolor='white',
        bgcolor='rgba(0,0,0,0)'
    )

    # Set title and layout
    title = 'Flight Route' if path_type == 'path' else f'World Tour ({len(path)} countries)'

    fig.update_layout(
        title=title,
        height=750,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='white'
    )

    return fig


# ============================================================================
# SECTION 12: INITIALIZATION AND LAUNCH
# ============================================================================

def initialize_widget(optimize_function, shortest_path_function):
    """
    Initialize widget with user's functions and load data.

    PARAMETERS:
        optimize_function: User's TSP optimization function
        shortest_path_function: User's shortest path function

    MODIFICATION TIP:
    - To use different data sources, modify load_flight_network() call
    - To preprocess data, add transformations after loading
    - To validate user functions, add function signature checks
    """
    widget_state['optimize_function'] = optimize_function
    widget_state['shortest_path_function'] = shortest_path_function

    # Load flight network data
    widget_state['flight_graph'], widget_state['country_info'], \
        widget_state['continents'], widget_state['flight_info'] = load_flight_network()


def launch_widget(optimize_function, shortest_path_function, port=5000):
    """
    Launch Flask server and open browser.

    PARAMETERS:
        optimize_function: User's TSP optimization function
        shortest_path_function: User's shortest path function
        port: Port number for server (default: 5000)

    MODIFICATION TIP:
    - To change port, pass different port parameter
    - To disable auto-browser opening, comment out the threading.Thread line
    - To add debug mode, change debug=False to debug=True in app.run()
    - To customize startup message, modify the print statements
    """
    # Initialize with user functions
    initialize_widget(optimize_function, shortest_path_function)

    # Determine platform and generate appropriate URL
    import os

    if 'WORKSPACE_ID' in os.environ:
        # Running on Coursera
        lab_id = os.environ['WORKSPACE_ID']
        url = f"https://{lab_id}.labs.coursera.org/flask/"
        platform = "coursera"
    elif 'HOSTNAME' in os.environ and 'REV_PROXY_BASE_DOMAIN' in os.environ:
        # Running on Learning Platform
        ip = os.environ['HOSTNAME'].split('.')[0][3:]
        url = os.environ['REV_PROXY_BASE_DOMAIN'].format(ip=ip, port=port)
        platform = "learning_platform"
    else:
        # Running on local machine
        url = f"http://localhost:{port}/"
        platform = "local"

    if platform in ("coursera", "learning_platform"):
        # Running in cloud environment - print the URL
        platform_name = "COURSERA LABS" if platform == "coursera" else "LEARNING PLATFORM"

        print(f"\n{'='*70}")
        print(f"🌍 World Tour & Flight Finder Widget")
        print(f"{'='*70}")
        print(f"\n✓ Server starting on port {port}")
        print(f"\n" + "!"*70)
        print(f"! IMPORTANT - {platform_name} ENVIRONMENT DETECTED")
        print(f"!"*70)
        print(f"\n⚠️  DO NOT use http://localhost:{port}/ or http://127.0.0.1:{port}/")
        print(f"\n✅ INSTEAD, OPEN THIS URL IN YOUR BROWSER:")
        print(f"\n   🔗 {url}")
        print(f"\n" + "="*70)
        print(f"\nCopy and paste the URL above into a new browser tab.")
        print(f"The widget will be accessible through the platform proxy.")
        print(f"{'='*70}\n")

        # Don't auto-open browser in cloud environments
    else:
        # Running locally - use localhost and print startup information
        def open_browser():
            import time
            time.sleep(1.5)
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()

        # Print startup information for local development
        print(f"\n{'='*70}")
        print(f"🌍 World Tour & Flight Finder Widget")
        print(f"{'='*70}")
        print(f"\n✓ Server starting at {url}")
        print(f"✓ Browser will open automatically...")
        print(f"\n📊 Flight Network Statistics:")
        print(f"   • {widget_state['flight_info']['total_countries']} countries")
        print(f"   • {widget_state['flight_info']['total_routes']} flight routes")
        print(f"   • {widget_state['flight_info']['density']*100:.1f}% network density")
        print(f"   • ${widget_state['flight_info']['avg_price']:.2f} average flight price")
        print(f"\n📝 Two Modes Available:")
        print(f"   1. SHORTEST PATH: Find cheapest route between two countries")
        print(f"   2. TSP TOUR: Find optimal tour visiting multiple countries")
        print(f"\n⚠️  To stop the server: Click the stop button (■) in the notebook toolbar")
        print(f"{'='*70}\n")

    # Run Flask server (bind to 0.0.0.0 to allow external access in containers)
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


# ============================================================================
# SECTION 13: MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("This server should be launched from the Jupyter notebook.")
    print("=" * 70)
    print("\nUsage:")
    print("    from utils import launch_tour_widget")
    print("    launch_tour_widget(optimize_world_tour, find_shortest_path)")
    print("\n" + "=" * 70)
