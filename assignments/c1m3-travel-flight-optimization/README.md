# C1M3 — Assignment: Building a Travel & Flight Optimization App

Graded lab for **Course 1, Module 3** of the *Generative AI for Software Development* specialization (DeepLearning.AI / Coursera).

Fictional context: implementing the core algorithms for **TravelOptima Inc.**, a travel planning platform:
1. **Smart Flight Finder** — cheapest flight route between two countries (shortest path).
2. **Tour Optimizer** — shortest tour visiting multiple destinations (TSP).

## Algorithms covered

| Problem                        | Small graph (~10 nodes)          | Large graph (thousands of nodes)           |
|--------------------------------|----------------------------------|--------------------------------------------|
| Shortest path (2 vertices)     | Dijkstra, direct search — O(V²)  | Dijkstra + priority queue (heapq) — O((V+E) log V) |
| Visit all vertices (TSP)       | Exact / backtracking — O(N!)     | Heuristics (Nearest Neighbor, 2-Opt)       |

## Files (as downloaded from the Lab, unmodified)

- `C1M3_Assignment.ipynb` — main notebook with exercises 1–3.
- `utils.py` — graph generation, JSON validation, plotting, tour widgets.
- `unittests.py` — local unit tests, run after each exercise.
- `submission_checker.py` — end-of-notebook check before submitting to the autograder.
- `tour_widget_server.py` — Flask server backing the tour visualizer widgets.

## Assets

Mirrored from the Lab environment as downloaded:

- `data/` — 6 CSVs: world/continents/americas country lists, distances, flights, tour countries.
- `images/` — `app.png` (visualization screenshot).
- `static/` — `tour_widget.html`, `widget_config.js` (Flask static assets).
- `templates/` — `tour_widget.html` (Flask Jinja template rendered by `render_template('tour_widget.html')` in `tour_widget_server.py`). Byte-identical to the copy in `static/`; both are kept as they exist in the Lab.

## Local workflow

1. Create/activate a Python 3.11/3.12 virtualenv at the repo root (`python3 -m venv .venv && source .venv/bin/activate`).
2. Install the assignment's dependencies as needed (`pip install jupyter flask networkx matplotlib` at minimum — inspect the imports in `utils.py` / `tour_widget_server.py` for the full list).
3. Launch Jupyter: `jupyter notebook` and open `C1M3_Assignment.ipynb`.
4. Solve each exercise, run the corresponding unittest cell until it passes.
5. Run `submission_checker.py` (or the corresponding notebook cell) as a final local check.
6. Copy the finished cells back into the Lab notebook on Coursera and click **Submit Assignment** for the autograder to score it.
