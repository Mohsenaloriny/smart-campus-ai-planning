"""
Smart Campus AI Planning System - Part I: Campus Route Planner
Course: Artificial Intelligence (CLO2) - Dr. Fayçal Hamdi

This module defines:
1. The Campus Graph (Locations, Coordinates, Weighted Edges).
2. Admissible Heuristic Function (Euclidean Straight-Line Distance).
3. Uniform-Cost Search (UCS).
4. A* Search.
5. Trace and Logging utilities for detailed analysis.
"""

import math
import heapq
from typing import Dict, List, Tuple, Optional, Any

# ==============================================================================
# 1. CAMPUS GRAPH SPECIFICATION
# ==============================================================================
# Requirement: At least 10 locations, 2D coordinates for heuristic calculation.
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
    "RES": (14.0, 10.0, "Research & Innovation Center") # 11th location
}

# Requirement: At least 15 weighted connections (edges) with positive costs.
# We define bidirectional connections with edge costs (representing travel cost/distance in hectometers/minutes).
# Note: Designed specifically so that shortest path by hops is NOT the lowest-cost path!
# For example: MG -> LIB -> CS is 2 hops (cost: 8 + 10 = 18)
# Whereas: MG -> ADM -> ENG -> CS is 3 hops (cost: 5 + 6 + 4 = 15) -> Fewer hops has HIGHER cost!
CAMPUS_EDGES: List[Tuple[str, str, float]] = [
    ("MG",  "PRK", 3.0),
    ("MG",  "ADM", 5.0),
    ("MG",  "LIB", 8.0),   # Direct but congested avenue (2 hops to CS, total 18)
    ("MG",  "MED", 4.0),
    ("PRK", "ADM", 3.0),
    ("ADM", "ENG", 6.0),
    ("ENG", "RES", 4.0),
    ("ENG", "CS",  4.0),
    ("RES", "CS",  3.0),
    ("LIB", "ENG", 5.0),
    ("LIB", "CS",  10.0),  # Highway segment
    ("LIB", "SC",  3.0),
    ("MED", "SC",  5.0),
    ("SC",  "CAF", 5.0),
    ("CAF", "CS",  7.0),
    ("CAF", "SPT", 5.0),
    ("CS",  "SPT", 6.0),
    ("ADM", "LIB", 5.0)
]

def build_adjacency_list() -> Dict[str, List[Tuple[str, float]]]:
    """Builds an undirected adjacency list from the edge list."""
    adj: Dict[str, List[Tuple[str, float]]] = {node: [] for node in CAMPUS_LOCATIONS}
    for u, v, w in CAMPUS_EDGES:
        adj[u].append((v, w))
        adj[v].append((u, w))
    # Sort neighbors alphabetically for deterministic execution
    for node in adj:
        adj[node].sort(key=lambda x: x[0])
    return adj

# ==============================================================================
# 2. HEURISTIC FUNCTION (EUCLIDEAN DISTANCE)
# ==============================================================================
def euclidean_heuristic(node: str, goal: str) -> float:
    """
    Calculates straight-line Euclidean distance h(n) between node and goal.
    Since straight-line distance is the shortest possible path between two points in 2D,
    h(n) <= h*(n), guaranteeing ADMISSIBILITY and CONSISTENCY.
    """
    x1, y1, _ = CAMPUS_LOCATIONS[node]
    x2, y2, _ = CAMPUS_LOCATIONS[goal]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def zero_heuristic(node: str, goal: str) -> float:
    """Trivial heuristic h(n) = 0 for A* (equivalent to UCS)."""
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
    """
    Uniform-Cost Search (UCS) on the campus graph.
    Priority Queue ordered by path cost g(n).
    Goal check occurs when a node is removed/expanded from the frontier.
    """
    adj = build_adjacency_list()
    
    # Priority queue stores tuples: (g_cost, counter, current_node, path)
    counter = 0
    frontier: List[Tuple[float, int, str, List[str]]] = []
    heapq.heappush(frontier, (0.0, counter, start, [start]))
    
    # Best-known g-cost to each state reached
    best_g: Dict[str, float] = {start: 0.0}
    explored: set = set()
    
    states_expanded = 0
    max_frontier_size = 1
    trace: List[Dict[str, Any]] = []

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        g_cost, _, current, path = heapq.heappop(frontier)

        # If already explored with a smaller or equal cost, skip
        if current in explored:
            continue

        # Log trace step
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

        # Goal test on expansion (crucial for optimality)
        if current == goal:
            return SearchResult(
                algorithm="Uniform-Cost Search (UCS)",
                start=start,
                goal=goal,
                path=path,
                cost=g_cost,
                states_expanded=states_expanded,
                max_frontier_size=max_frontier_size,
                trace=trace
            )

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
    """
    A* Search on the campus graph.
    Priority Queue ordered by evaluation function f(n) = g(n) + h(n).
    Goal check occurs when a node is removed/expanded from the frontier.
    """
    adj = build_adjacency_list()
    
    counter = 0
    # Frontier stores: (f_cost, g_cost, counter, current_node, path)
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

        # Goal test on expansion
        if current == goal:
            return SearchResult(
                algorithm="A* Search",
                start=start,
                goal=goal,
                path=path,
                cost=g_cost,
                states_expanded=states_expanded,
                max_frontier_size=max_frontier_size,
                trace=trace
            )

        explored.add(current)

        for neighbor, edge_cost in adj[current]:
            new_g = g_cost + edge_cost
            if neighbor not in explored:
                if neighbor not in best_g or new_g < best_g[neighbor]:
                    best_g[neighbor] = new_g
                    h_val = heuristic_func(neighbor, goal)
                    new_f = new_g + h_val
                    counter += 1
                    heapq.heappush(frontier, (new_f, new_g, counter, neighbor, path + [neighbor]))

    return SearchResult("A* Search", start, goal, None, float('inf'), states_expanded, max_frontier_size, trace)

if __name__ == "__main__":
    print("Testing Campus Graph & Search Algorithms:")
    start_node = "MG"
    goal_node = "CS"
    
    res_ucs = uniform_cost_search(start_node, goal_node)
    print("\n" + res_ucs.summary())
    
    res_astar = a_star_search(start_node, goal_node)
    print("\n" + res_astar.summary())

