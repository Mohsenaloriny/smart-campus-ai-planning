"""
Smart Campus AI Planning System - Part I: Campus Route Planner
Course: Artificial Intelligence (CLO2) - Dr. Fayçal Hamdi

This module defines:
1. The Campus Graph (11 Locations, Coordinates, 18 Weighted Edges).
   Note: Every edge weight w(u, v) >= Euclidean(u, v), guaranteeing that
   the Euclidean straight-line distance heuristic is STRICTLY ADMISSIBLE
   (h(n) <= h*(n)) and CONSISTENT across all 121 node pairs.
2. Admissible Euclidean Heuristic Function.
3. Uniform-Cost Search (UCS).
4. A* Search.
5. Trace and Logging utilities.
"""

import math
import heapq
from typing import Dict, List, Tuple, Optional, Any

# ==============================================================================
# 1. CAMPUS GRAPH SPECIFICATION
# ==============================================================================
CAMPUS_LOCATIONS: Dict[str, Tuple[float, float, str]] = {
    "MG":  (0.0, 5.0,  "Main Gate"),
    "ADM": (4.0, 9.0,  "Administration Building"),
    "ENG": (11.0, 9.0, "College of Engineering"),
    "CS":  (15.0, 7.0, "College of Computer Science"),
    "LIB": (7.0, 5.0,  "Central Library"),
    "SC":  (6.0, 2.0,  "Student Center"),
    "CAF": (11.0, 3.0, "Main Cafeteria"),
    "SPT": (16.0, 2.0, "Sports Complex"),
    "MED": (2.0, 1.0,  "Medical Center"),
    "PRK": (1.0, 8.0,  "Main Parking Hub"),
    "RES": (14.0, 10.0, "Research & Innovation Lab")
}

# Every edge weight w >= Euclidean distance of endpoints:
# e.g., MG (0,5) to ADM (4,9): Euclidean = sqrt(32) = 5.66 -> Edge weight = 6.0
# ADM (4,9) to ENG (11,9): Euclidean = 7.00 -> Edge weight = 7.0
# ENG (11,9) to CS (15,7): Euclidean = sqrt(20) = 4.47 -> Edge weight = 5.0
# MG -> ADM -> ENG -> CS = 6 + 7 + 5 = 18.0 (3 hops)
# MG -> LIB -> CS = 9 + 12 = 21.0 (2 hops) -> Hop-count vs Cost inversion preserved!
CAMPUS_EDGES: List[Tuple[str, str, float]] = [
    ("MG",  "PRK", 4.0),
    ("MG",  "ADM", 6.0),
    ("MG",  "LIB", 9.0),   # Congested central boulevard
    ("MG",  "MED", 5.0),
    ("PRK", "ADM", 4.0),
    ("ADM", "ENG", 7.0),
    ("ENG", "RES", 4.0),
    ("ENG", "CS",  5.0),
    ("RES", "CS",  4.0),
    ("LIB", "ENG", 6.0),
    ("LIB", "CS",  12.0),  # Highway avenue: 2 hops from MG to CS (cost: 9+12=21)
    ("LIB", "SC",  4.0),
    ("MED", "SC",  5.0),
    ("SC",  "CAF", 6.0),
    ("CAF", "CS",  7.0),
    ("CAF", "SPT", 6.0),
    ("CS",  "SPT", 6.0),
    ("ADM", "LIB", 5.0)
]

def build_adjacency_list() -> Dict[str, List[Tuple[str, float]]]:
    """Builds an undirected adjacency list from the edge list."""
    adj: Dict[str, List[Tuple[str, float]]] = {node: [] for node in CAMPUS_LOCATIONS}
    for u, v, w in CAMPUS_EDGES:
        adj[u].append((v, w))
        adj[v].append((u, w))
    for node in adj:
        adj[node].sort(key=lambda x: x[0])
    return adj

# ==============================================================================
# 2. HEURISTIC FUNCTIONS
# ==============================================================================
def euclidean_heuristic(node: str, goal: str) -> float:
    """
    Calculates straight-line Euclidean distance h(n) between node and goal.
    Since w(u, v) >= Euclidean(u, v) for all edges, by the triangle inequality,
    h(n) <= h*(n) strictly holds for all node pairs (Guaranteed Admissibility).
    """
    x1, y1, _ = CAMPUS_LOCATIONS[node]
    x2, y2, _ = CAMPUS_LOCATIONS[goal]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def zero_heuristic(node: str, goal: str) -> float:
    """Trivial zero heuristic h(n) = 0 for A* (identical to UCS)."""
    return 0.0

# ==============================================================================
# 3. SEARCH ALGORITHMS & TRACE ENGINE
# ==============================================================================
class SearchResult:
    def __init__(self, algorithm: str, start: str, goal: str, path: Optional[List[str]],
                 cost: float, states_expanded: int, max_frontier_size: int, trace: List[Dict[str, Any]]):
        self.algorithm = algorithm
        self.start = start
        self.goal = goal
        self.path = path
        self.cost = cost
        self.states_expanded = states_expanded
        self.max_frontier_size = max_frontier_size
        self.trace = trace

    def summary(self) -> str:
        path_str = " -> ".join(self.path) if self.path else "No Path Found"
        return (f"[{self.algorithm}] Start: {self.start} | Goal: {self.goal}\n"
                f"  - Solution Path: {path_str}\n"
                f"  - Total Cost: {self.cost:.2f}\n"
                f"  - States Expanded: {self.states_expanded}\n"
                f"  - Max Frontier Size: {self.max_frontier_size}")

def uniform_cost_search(start: str, goal: str) -> SearchResult:
    adj = build_adjacency_list()
    counter = 0
    frontier: List[Tuple[float, int, str, List[str]]] = []
    heapq.heappush(frontier, (0.0, counter, start, [start]))
    best_g: Dict[str, float] = {start: 0.0}
    explored: set = set()
    states_expanded = 0
    max_frontier_size = 1
    trace: List[Dict[str, Any]] = []

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        g_cost, _, current, path = heapq.heappop(frontier)
        if current in explored:
            continue

        states_expanded += 1
        frontier_snapshot = [(f"{item[2]}(g={item[0]:.1f})") for item in frontier]
        trace.append({
            "step": states_expanded,
            "expanded_node": current,
            "g": g_cost,
            "h": 0.0,
            "f": g_cost,
            "path": list(path),
            "frontier": frontier_snapshot
        })

        if current == goal:
            return SearchResult("Uniform-Cost Search (UCS)", start, goal, path, g_cost, states_expanded, max_frontier_size, trace)

        explored.add(current)
        for neighbor, edge_cost in adj[current]:
            new_g = g_cost + edge_cost
            if neighbor not in explored:
                if neighbor not in best_g or new_g < best_g[neighbor]:
                    best_g[neighbor] = new_g
                    counter += 1
                    heapq.heappush(frontier, (new_g, counter, neighbor, path + [neighbor]))

    return SearchResult("Uniform-Cost Search (UCS)", start, goal, None, float('inf'), states_expanded, max_frontier_size, trace)

def a_star_search(start: str, goal: str, heuristic_func=euclidean_heuristic) -> SearchResult:
    adj = build_adjacency_list()
    counter = 0
    initial_h = heuristic_func(start, goal)
    frontier: List[Tuple[float, float, int, str, List[str]]] = []
    heapq.heappush(frontier, (initial_h, 0.0, counter, start, [start]))
    best_g: Dict[str, float] = {start: 0.0}
    explored: set = set()
    states_expanded = 0
    max_frontier_size = 1
    trace: List[Dict[str, Any]] = []

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        f_cost, g_cost, _, current, path = heapq.heappop(frontier)
        if current in explored:
            continue

        states_expanded += 1
        current_h = heuristic_func(current, goal)
        frontier_snapshot = [(f"{item[3]}(f={item[0]:.1f},g={item[1]:.1f})") for item in frontier]
        trace.append({
            "step": states_expanded,
            "expanded_node": current,
            "g": g_cost,
            "h": current_h,
            "f": f_cost,
            "path": list(path),
            "frontier": frontier_snapshot
        })

        if current == goal:
            return SearchResult("A* Search", start, goal, path, g_cost, states_expanded, max_frontier_size, trace)

        explored.add(current)
        for neighbor, edge_cost in adj[current]:
            new_g = g_cost + edge_cost
            if neighbor not in explored:
                if neighbor not in best_g or new_g < best_g[neighbor]:
                    best_g[neighbor] = new_g
                    h_val = heuristic_func(neighbor, goal)
                    counter += 1
                    heapq.heappush(frontier, (new_g + h_val, new_g, counter, neighbor, path + [neighbor]))

    return SearchResult("A* Search", start, goal, None, float('inf'), states_expanded, max_frontier_size, trace)

if __name__ == "__main__":
    res_ucs = uniform_cost_search("MG", "CS")
    print(res_ucs.summary())
    res_astar = a_star_search("MG", "CS")
    print(res_astar.summary())
