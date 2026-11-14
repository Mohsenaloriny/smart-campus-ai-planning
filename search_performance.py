"""
Smart Campus AI Planning System - Part II: Search Performance Investigation
Course: Artificial Intelligence (CLO3) - Dr. Fayçal Hamdi

Run controlled benchmarks on the campus graph.
"""
from campus_graph import (
    a_star_search, euclidean_heuristic,
    uniform_cost_search, zero_heuristic,
)

# ==============================================================================
# 1. BENCHMARK PAIRS & HEURISTIC CONFIGURATION
# ==============================================================================
PAIRS = [("MG", "CS"), ("MED", "SPT"), ("LIB", "SC")]
# ==============================================================================
# 2. CONTROLLED EXPERIMENTS
# ==============================================================================
def run_experiments():
    """Yield each result in a fixed order on the original campus graph."""
    for start, goal in PAIRS:
        yield "UCS", uniform_cost_search(start, goal)
        for label, heuristic in [
            ("A* (zero)", zero_heuristic),
            ("A* (Euclidean)", euclidean_heuristic),
        ]:
            yield label, a_star_search(start, goal, heuristic)


# ==============================================================================
# 3. RESULTS TABLE
# ==============================================================================
def print_results():
    print("| Pair | Strategy | Path | Cost | Expanded | Peak frontier |")
    print("| --- | --- | --- | ---: | ---: | ---: |")
    for label, result in run_experiments():
        path = " → ".join(result.path)
        print(
            f"| {result.start} → {result.goal} | {label} | {path} | "
            f"{result.cost:g} | {result.states_expanded} | {result.max_frontier_size} |"
        )


if __name__ == "__main__":
    print_results()
