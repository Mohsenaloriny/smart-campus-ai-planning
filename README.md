# Smart Campus AI Planning System
> **Artificial Intelligence Group Project**  
> **Course Supervision:** Dr. Fayçal Hamdi — Faculty of Computer and Information Systems  
> **Assessed Learning Outcomes:** CLO2 (Search Strategies) · CLO3 (Search Performance) · CLO4 (Constraint Satisfaction Problems)

---

## 📌 Project Overview
The **Smart Campus AI Planning System** is an integrated AI decision-support platform designed to address two central operational challenges on a modern university campus:
1. **Intelligent Route Planning & Search Optimization (CLO2 & CLO3):** Finding cost-optimal paths between campus facilities using uninformed and heuristic search strategies, with experimental evaluation of search performance.
2. **Campus Resource & Schedule Allocation (CLO4):** Solving complex timetable, classroom, and activity scheduling problems as Constraint Satisfaction Problems (CSPs).

---

## 🏛️ Part I — Campus Route Planner (Implemented)
Part I models the campus environment as a weighted spatial graph and implements search algorithms to navigate between facilities.

### Topological Specifications:
* **11 Distinct Campus Facilities** with 2D Cartesian coordinates $(x, y)$ on a $100\text{m}$ grid.
* **18 Weighted Bidirectional Pathways** with positive transit costs.
* **Topological Inversion Verified:** Demonstrates why hop-count minimization (BFS) fails; the 2-hop route (`MG -> LIB -> CS`, cost: $18.0$) is strictly more expensive than the optimal 3-hop route (`MG -> ADM -> ENG -> CS`, cost: $15.0$).

### Search Algorithms & Heuristic Design:
* **Uniform-Cost Search (UCS):** Uninformed cost-optimal search expanding states in non-decreasing order of $g(n)$.
* **A* Search:** Informed search driven by evaluation function $f(n) = g(n) + h(n)$.
* **Euclidean Heuristic $h(n)$:** Straight-line 2D Euclidean distance $h(n) = \sqrt{(x_n - x_G)^2 + (y_n - y_G)^2}$.
  * **Admissible ($h(n) \le h^*(n)$):** In physical 2D space, straight-line distance is the infimum of all physical trajectories; hence, it never overestimates actual road costs.
  * **Consistent (Monotonic):** Satisfies triangle inequality $h(n) \le c(n, a, n') + h(n')$.

### Benchmark Results (`MG` $\rightarrow$ `CS`):
| Search Strategy | Optimal Path | Total Path Cost | Expanded States | Search Effort Reduction |
| :--- | :--- | :---: | :---: | :---: |
| **Uniform-Cost Search (UCS)** | `MG -> ADM -> ENG -> CS` | **15.00** | 9 states | Baseline |
| **A* Search (Euclidean)** | `MG -> ADM -> ENG -> CS` | **15.00** | **4 states** | **-55.6% expansions** |

---

## 📂 Repository Structure
```text
smart-campus-ai-planning/
├── README.md                               # Project documentation and guide
├── requirements.txt                        # Python dependencies
├── .gitignore                              # Git exclusion rules
├── campus_graph.py                         # Core graph model, UCS, A*, and tracing module
├── AI_Project_Part1_Report.ipynb           # Complete Jupyter Notebook with pre-rendered plots & traces
├── AI_Project_Part1_Route_Planner.ipynb    # Executable routing experiments notebook
└── Report_Part1_Campus_Route_Planner.md    # Formal academic report for Part I (CLO2)
```

---

## 🚀 Quickstart & Setup

### Prerequisites
Clone this repository:
```bash
git clone https://github.com/Mohsenaloriny/smart-campus-ai-planning.git
cd smart-campus-ai-planning
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Run Python Search Module
```bash
python campus_graph.py
```

### Open Jupyter Notebook
Launch the notebook in VS Code or JupyterLab:
```bash
jupyter notebook AI_Project_Part1_Report.ipynb
```

---

## 👥 Group Collaboration Roadmap
* **Student A (Completed):** Part I — Problem formulation, campus graph topology, Euclidean heuristic design & proofs, UCS and A* implementations, and step-by-step trace tables.
* **Student B (Upcoming):** Part III — Campus Scheduling CSP formulation $(X, D, C)$, Backtracking Search, MRV, Degree Heuristic, LCV, and Forward Checking.
* **Student C (Upcoming):** Part II — Empirical search performance experiments (3 start-goal pairs, heuristic sensitivity analysis, visualization plots).
