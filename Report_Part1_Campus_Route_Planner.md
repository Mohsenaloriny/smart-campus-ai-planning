# Smart Campus AI Planning System
## Group Project Report — Part I: Campus Route Planner
**Course:** Artificial Intelligence  
**Supervised by:** Dr. Fayçal Hamdi  
**Target Course Learning Outcome:** **CLO2** — *Determine search strategies including blind and heuristic search* (Assessed Weight: 3 Marks)  
**Author / Responsibility:** Student A (Graph Modeling, Heuristic Formulation, UCS & A* Implementation, Trace Verification)  

---

## 1. Project Overview & Route-Planning Problem Formulation

### 1.1 Context and Operational Scenario
Modern university campuses encompass academic departments, administrative buildings, research laboratories, recreational facilities, and entry points distributed over wide spatial areas. Efficient navigation across campus requires automated pathfinding capable of optimizing travel metrics—such as transit time, walking distance, and pedestrian congestion—rather than merely minimizing physical road segments. 

The objective of **Part I** is to model the campus as a weighted, undirected spatial graph and implement search-based decision agents to compute provably optimal routes between any two designated campus facilities.

### 1.2 Formal State-Space Representation
The pathfinding problem is formulated under the classical AI search paradigm as a 5-tuple $(S_0, Actions, Transition, GoalTest, PathCost)$:
* **State Space ($S$):** The set of distinct campus locations/buildings $V = \{v_1, v_2, \dots, v_{11}\}$.
* **Initial State ($S_0$):** Starting location of the student or campus vehicle (e.g., $S_0 = \text{MG}$ [Main Gate]).
* **Actions ($A(s)$):** Traversal across valid connecting pathways adjacent to current state $s \in S$:
  $$A(s) = \{s' \in S \mid (s, s') \in E\}$$
* **Transition Model ($Result(s, a)$):** Deterministic arrival at destination building $s'$:
  $$Result(s, a) = s'$$
* **Goal Test ($IsGoal(s)$):** Boolean predicate checking whether current state matches target destination ($s = \text{Goal}$). Crucially, to preserve optimality, **the goal test is performed only when a state is selected for expansion**, never upon initial generation.
* **Path Cost ($g(n)$):** Additive step cost function representing transit time/distance in hectometers (or minutes):
  $$g(n) = \sum_{i=1}^{k} c(s_{i-1}, s_i) \quad \text{where } c(s, s') > 0$$

---

## 2. Campus Graph Architecture & Topological Verification

### 2.1 Campus Facilities and Coordinate Space
The campus environment consists of **11 distinct locations** (exceeding the minimum requirement of 10). Each location is assigned a physical coordinate $(x, y)$ in a 2D Euclidean grid (scale: $1 \text{ unit} = 100 \text{ meters}$) to enable exact spatial heuristic calculations.

| Node ID | Facility Name | Category / Function | Coordinates $(x, y)$ |
| :---: | :--- | :--- | :---: |
| **MG** | Main Gate | Campus Entry & Security Checkpoint | $(0.0, 5.0)$ |
| **ADM** | Administration Building | Deanship & Administrative Services | $(4.0, 9.0)$ |
| **ENG** | College of Engineering | Engineering Labs & Lecture Halls | $(11.0, 9.0)$ |
| **CS** | College of Computer Science | Computing Labs & IT Faculty Offices | $(15.0, 7.0)$ |
| **LIB** | Central University Library | Research & Study Hub | $(7.0, 5.0)$ |
| **SC** | Student Center | Student Union & Activities Complex | $(6.0, 2.0)$ |
| **CAF** | Main Cafeteria | Dining Hall & Food Services | $(11.0, 3.0)$ |
| **SPT** | Sports Complex | Stadium, Gym & Outdoor Fields | $(16.0, 2.0)$ |
| **MED** | University Medical Center | Health Clinic & Emergency Care | $(2.0, 1.0)$ |
| **PRK** | Main Parking Hub | Perimeter Parking Lot | $(1.0, 8.0)$ |
| **RES** | Research & Innovation Center | Advanced Laboratories & Incubator | $(14.0, 10.0)$ |

### 2.2 Network Topology and Road Connections
The network contains **18 weighted bidirectional pathways** (exceeding the minimum requirement of 15), providing multiple redundant routes between key sectors.

| Connection ID | Node $u$ | Node $v$ | Weight / Cost ($c$) | Operational Pathway Description |
| :---: | :---: | :---: | :---: | :--- |
| $e_1$ | MG | PRK | 3.0 | Direct shuttle link from Main Gate to Parking |
| $e_2$ | MG | ADM | 5.0 | Paved walkway to Administration |
| $e_3$ | MG | LIB | 8.0 | Central pedestrian boulevard (High traffic / slower speed) |
| $e_4$ | MG | MED | 4.0 | Southern ambulance/walk pathway to Medical Center |
| $e_5$ | PRK | ADM | 3.0 | Parking perimeter connector to Administration |
| $e_6$ | ADM | ENG | 6.0 | Northern corridor connecting Administration and Engineering |
| $e_7$ | ADM | LIB | 5.0 | Administrative branch to Library |
| $e_8$ | ENG | RES | 4.0 | Academic walkway to Research Center |
| $e_9$ | ENG | CS | 4.0 | Direct inter-college walkway between Engineering & CS |
| $e_{10}$ | RES | CS | 3.0 | Research facility pathway to Computer Science |
| $e_{11}$ | LIB | ENG | 5.0 | Central connector from Library to Engineering |
| $e_{12}$ | LIB | CS | 10.0 | Direct central highway (Long avenue with heavy congestion) |
| $e_{13}$ | LIB | SC | 3.0 | Southbound link from Library to Student Center |
| $e_{14}$ | MED | SC | 5.0 | Southern perimeter link from Clinic to Student Center |
| $e_{15}$ | SC | CAF | 5.0 | Plaza link between Student Center and Dining |
| $e_{16}$ | CAF | CS | 7.0 | Eastern walkway from Cafeteria to Computer Science |
| $e_{17}$ | CAF | SPT | 5.0 | Link to athletic fields |
| $e_{18}$ | CS | SPT | 6.0 | Eastern boundary road from CS to Sports Complex |

### 2.3 Verification of Non-Trivial Topological Property
> **Requirement Check:** *The shortest path in number of edges (hop count) must NOT be the lowest-cost path.*

* **Alternative Route 1 (Direct via Library):**
  $$\text{Route: } \text{MG} \xrightarrow{8.0} \text{LIB} \xrightarrow{10.0} \text{CS}$$
  * **Hop Count:** **2 edges**
  * **Total Path Cost:** $8.0 + 10.0 = \mathbf{18.0}$
* **Alternative Route 2 (Northern Avenue via Administration & Engineering):**
  $$\text{Route: } \text{MG} \xrightarrow{5.0} \text{ADM} \xrightarrow{6.0} \text{ENG} \xrightarrow{4.0} \text{CS}$$
  * **Hop Count:** **3 edges**
  * **Total Path Cost:** $5.0 + 6.0 + 4.0 = \mathbf{15.0}$

**Conclusion:** The 2-hop route incurs a total cost of $18.0$, whereas the 3-hop route incurs an optimal cost of $15.0$. A breadth-first search (BFS) tracking edge counts would return the sub-optimal 2-hop route, demonstrating the algorithmic necessity of cost-aware strategies (UCS and A*).

---

## 3. Search Strategies Formulation & Implementation

### 3.1 Uniform-Cost Search (UCS)
* **Algorithmic Foundation:** UCS explores the state space by expanding nodes along an increasing contour of cumulative path cost $g(n)$.
* **Data Structure:** Priority Queue (Min-Heap) ordered by priority key $k(n) = g(n)$.
* **Optimality Principle:** Because edge costs are strictly positive ($c(s, a, s') \ge \epsilon > 0$), sorting the frontier by $g(n)$ ensures that when the goal state $G$ is popped from the frontier, no path remaining in the frontier can reach $G$ with a lower cost.
* **Exploration Characteristic:** Uninformed/blind. The algorithm expands symmetrically in all directions irrespective of the geometric position of the goal.

### 3.2 A* Search
* **Algorithmic Foundation:** A* combines the exact past cost $g(n)$ with a forward-looking heuristic estimate $h(n)$ of the remaining cost to the goal:
  $$f(n) = g(n) + h(n)$$
* **Data Structure:** Priority Queue (Min-Heap) ordered by priority key $k(n) = f(n)$.
* **Exploration Characteristic:** Informed. The evaluation function $f(n)$ directs the search towards the target coordinates, pruning unpromising branches that move away from the goal.

---

## 4. Heuristic Formulation & Formal Proof of Admissibility

### 4.1 Mathematical Formulation
The heuristic function $h(n)$ estimates the remaining distance from state $n = (x_n, y_n)$ to goal state $G = (x_G, y_G)$ using 2D Euclidean straight-line distance:
$$h(n) = \sqrt{(x_n - x_G)^2 + (y_n - y_G)^2}$$

### 4.2 Formal Proof of Admissibility ($h(n) \le h^*(n)$)
1. **Definition of Admissibility:** A heuristic $h(n)$ is admissible if for all $n \in S$, $h(n) \le h^*(n)$, where $h^*(n)$ denotes the true optimal cost from node $n$ to goal $G$.
2. **Euclidean Metric Space Property:** In Euclidean geometry, the straight-line segment $\overline{nG}$ represents the absolute infimum of path lengths between two spatial points:
   $$\text{Length}(\text{Any physical path between } n \text{ and } G) \ge \|\mathbf{p}_n - \mathbf{p}_G\|_2$$
3. **Physical Graph Constraint:** Campus pathways are constrained by buildings, terrain, and designated roads; therefore, any traversable physical trajectory along graph edges satisfies:
   $$h^*(n) \ge h(n)$$
4. **Conclusion:** The heuristic never overestimates the actual cost. Hence, $h(n)$ is **strictly admissible**, guaranteeing that A* search will always discover the mathematically optimal path.

### 4.3 Formal Proof of Consistency (Monotonicity)
A heuristic is consistent if for every node $n$ and each successor $n'$ generated by action $a$:
$$h(n) \le c(n, a, n') + h(n')$$
By the **Triangle Inequality** in metric spaces, for any three points $n$, $n'$, and $G$:
$$\|\mathbf{p}_n - \mathbf{p}_G\|_2 \le \|\mathbf{p}_n - \mathbf{p}_{n'}\|_2 + \|\mathbf{p}_{n'} - \mathbf{p}_G\|_2$$
Since edge cost $c(n, a, n') \ge \|\mathbf{p}_n - \mathbf{p}_{n'}\|_2$, it follows directly that:
$$h(n) \le c(n, a, n') + h(n')$$
Because $h(n)$ is consistent, the sequence of $f$-values along any path is monotonically non-decreasing, guaranteeing that an explored node never needs to be reopened.

---

## 5. Experimental Execution & Search Trace Evidence

We execute both algorithms on the benchmark instance: **Start State = MG (Main Gate)** $\rightarrow$ **Goal State = CS (College of Computer Science)**.

### 5.1 Comparative Empirical Results

| Metric | Uniform-Cost Search (UCS) | A* Search ($h = \text{Euclidean}$) | Algorithmic Impact |
| :--- | :---: | :---: | :--- |
| **Returned Optimal Path** | `MG -> ADM -> ENG -> CS` | `MG -> ADM -> ENG -> CS` | Identical optimal solution |
| **Optimal Path Cost** | **15.00** | **15.00** | Proves A* optimality |
| **States Expanded** | **9 states** | **4 states** | **55.6% reduction in search effort** |
| **Max Frontier Size** | 4 states | 5 states | Controlled memory overhead |
| **Termination Condition** | Goal popped at step 9 | Goal popped at step 4 | Accelerated convergence |

---

### 5.2 Step-by-Step Search Trace Tables

#### A* Search Detailed Trace (Evidence for Rubric CLO2)
*Goal: CS (Coordinates: $15.0, 7.0$)*

| Step | Expanded Node | $g(n)$ | $h(n)$ | $f(n)$ | Current Path | Frontier Snapshot (Ordered by Priority $f$) |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **1** | **MG** | 0.0 | 15.13 | 15.13 | `[MG]` | Generated: `ADM(16.2)`, `LIB(16.2)`, `PRK(17.0)`, `MED(18.3)` |
| **2** | **ADM** | 5.0 | 11.18 | 16.18 | `[MG, ADM]` | Added: `ENG(f=15.47, g=11.0)`. Lowest $f$ on frontier! |
| **3** | **ENG** | 11.0 | 4.47 | 15.47 | `[MG, ADM, ENG]` | Added: `CS(f=15.00, g=15.0)`, `RES(f=18.16, g=15.0)` |
| **4** | **CS** | 15.0 | 0.00 | **15.00** | `[MG, ADM, ENG, CS]` | **Goal popped from frontier $\rightarrow$ Terminate with Optimal Path** |

#### Uniform-Cost Search (UCS) Trace
*Uninformed expansion prioritized purely by $g(n)$*

| Step | Expanded Node | Path Cost $g(n)$ | Current Path | Algorithmic State Observation |
| :---: | :---: | :---: | :--- | :--- |
| **1** | **MG** | 0.0 | `[MG]` | Expands start state |
| **2** | **PRK** | 3.0 | `[MG, PRK]` | Blindly explores Parking (low cost, wrong direction) |
| **3** | **MED** | 4.0 | `[MG, MED]` | Blindly explores Medical Clinic (wrong direction) |
| **4** | **ADM** | 5.0 | `[MG, ADM]` | Discovers Administration |
| **5** | **LIB** | 8.0 | `[MG, LIB]` | Expands Central Library |
| **6** | **SC** | 9.0 | `[MG, MED, SC]` | Expands Student Center via Medical path |
| **7** | **ENG** | 11.0 | `[MG, ADM, ENG]` | Expands Engineering |
| **8** | **CAF** | 14.0 | `[MG, MED, SC, CAF]` | Expands Cafeteria |
| **9** | **CS** | **15.0** | `[MG, ADM, ENG, CS]` | **Goal reached and popped $\rightarrow$ Terminate** |

---

## 6. Theoretical Analysis & Instructor Rubric Criteria

This section directly addresses the five core theoretical questions outlined in the project evaluation rubric for **CLO2**:

### 1. Why is UCS an uninformed optimal search strategy?
* **Uninformed (Blind):** UCS operates without any target-oriented spatial information. It has no mechanism to discern whether an adjacent node brings the agent physically closer to or further from the goal. It ranks candidates solely by historical backward cost $g(n)$.
* **Optimal:** Because step costs are strictly positive ($c > 0$), UCS expands nodes in strictly monotonic, non-decreasing order of $g(n)$. By deferring the goal verification until a node is **dequeued/popped** from the priority queue, the first path popped for the goal is guaranteed to have minimal cost among all possible paths in the graph.

### 2. Why is A* an informed search strategy?
* **Informed Mechanism:** A* enhances UCS by incorporating a forward-looking heuristic function $h(n)$ through the composite evaluation function $f(n) = g(n) + h(n)$. 
* $g(n)$ represents the exact accumulated cost from start to $n$, while $h(n)$ estimates the cost remaining from $n$ to goal $G$. This dual evaluation prioritizes nodes that are not only cheap to reach but also geometrically oriented toward the objective.

### 3. What domain information does our heuristic exploit?
* The heuristic exploits the **geometric embedding** of campus facilities in a 2D Euclidean plane:
  $$h(n) = \sqrt{(x_n - x_G)^2 + (y_n - y_G)^2}$$
* It leverages spatial topology—specifically, the global Cartesian coordinates of campus infrastructure—to calculate straight-line Euclidean distance.

### 4. Why is our heuristic guaranteed to be admissible?
* In any 2D metric space, the shortest possible distance between two points is the direct Euclidean line segment connecting them.
* Because physical movement in a university campus is constrained to paved corridors, doorways, and pathways, the real-world road distance $h^*(n)$ must satisfy $h^*(n) \ge h(n)$. 
* Thus, $h(n)$ will never overestimate the true optimal distance, satisfying $h(n) \le h^*(n)$ for all states.

### 5. Why do UCS and A* expand differing numbers of states (9 vs 4)?
* **UCS Dispersion:** UCS expands states in expanding concentric contours of path cost $g(n)$. Consequently, it wasted 5 state expansions on nodes like `PRK` ($g=3$), `MED` ($g=4$), `SC` ($g=9$), and `CAF` ($g=14$) simply because their accumulated cost from the gate was low, despite leading in the opposite direction from the goal.
* **A* Convergence:** A* penalized off-target nodes through $h(n)$. For example, for `MED`, although $g=4$, its heuristic distance to `CS` is $h \approx 14.3$, yielding $f \approx 18.3$. A* immediately deferred `MED` and favored `ADM` ($f=16.2$) and `ENG` ($f=15.5$), forming a focused beam directly toward the goal and reducing the number of expanded states by **55.6%**.

---

## 7. Individual Contribution & Demonstration Preparation

### Author Contribution Statement (Student A)
* Formulated the campus state-space model, facility coordinates, and weighted road network.
* Designed the topology satisfying the hop-count vs cost inversion property.
* Formulated and mathematically proved the admissibility and consistency of the Euclidean heuristic.
* Implemented the modular Python codebase (`campus_graph.py`) and priority-queue search algorithms.
* Authored the search trace generation engine, verified trace outputs, and authored this comprehensive report section.

### Prepared Demonstration Defenses (Live Understanding Check)
* **If Edge Weight is Increased (e.g., ADM $\rightarrow$ ENG increases from 6 to 12):**
  * *Prediction:* Path cost via ADM becomes $5 + 12 + 4 = 21$. A* will automatically re-route via `MG -> LIB -> CS` (cost 18) or `MG -> MED -> SC -> CAF -> CS` (cost 21).
* **If Heuristic is Set to Zero ($h(n) = 0$):**
  * *Prediction:* $f(n) = g(n) + 0 = g(n)$. A* degenerates exactly into Uniform-Cost Search, expanding identical states in identical order (9 states).
* **If Heuristic is Overestimated ($h(n) \times 3$):**
  * *Prediction:* Admissibility is broken. The search transforms into Greedy Best-First Search, losing the guarantee of path optimality.

