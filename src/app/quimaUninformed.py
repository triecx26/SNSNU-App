import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import time
from collections import deque

# ----- Graph definition -----
directed_graph = {
    'A': [('B', 2), ('C', 5)],
    'B': [('D', 3), ('E', 4)],
    'C': [('F', 2), ('G', 3)],
    'D': [('H', 2), ('I', 3)],
    'E': [('J', 4), ('K', 1)],
    'F': [('L', 2), ('M', 3)],
    'G': [('N', 5), ('O', 1)],
    'H': [], 'I': [], 'J': [], 'K': [],
    'L': [], 'M': [], 'N': [], 'O': []
}

# Build undirected graph
graph = {node: [] for node in directed_graph}
for u, neighbors in directed_graph.items():
    for v, w in neighbors:
        graph[u].append((v, w))
        graph[v].append((u, w))

# ----- Node positions -----
def scale_pos(pos, scale=0.7):
    return (int(pos[0] * scale), int(pos[1] * scale))

node_positions = {
    'A': scale_pos((500, 50)),
    'B': scale_pos((300, 150)), 'C': scale_pos((700, 150)),
    'D': scale_pos((200, 250)), 'E': scale_pos((400, 250)),
    'F': scale_pos((600, 250)), 'G': scale_pos((800, 250)),
    'H': scale_pos((120, 350)), 'I': scale_pos((280, 350)),
    'J': scale_pos((420, 350)), 'K': scale_pos((480, 350)),
    'L': scale_pos((600, 350)), 'M': scale_pos((660, 350)),
    'N': scale_pos((760, 350)), 'O': scale_pos((820, 350)),
}

# ----- Utility -----
def compute_depth(start, goal):
    if start == goal:
        return 0
    q = deque([(start, 0)])
    visited = {start}
    while q:
        node, depth = q.popleft()
        for neigh, _ in graph[node]:
            if neigh == goal:
                return depth + 1
            if neigh not in visited:
                visited.add(neigh)
                q.append((neigh, depth + 1))
    return None

# ---------------- Search Algorithms ----------------
def bfs_steps(start, goal):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        yield node, path
        if node == goal:
            return
        if node not in visited:
            visited.add(node)
            for neighbor, _ in graph[node]:
                if neighbor not in visited:
                    queue.append(path + [neighbor])

def dfs_steps(start, goal):
    stack = [[start]]
    visited = set()
    while stack:
        path = stack.pop()
        node = path[-1]
        yield node, path
        if node == goal:
            return
        if node not in visited:
            visited.add(node)
            for neighbor, _ in reversed(graph[node]):
                if neighbor not in path:
                    stack.append(path + [neighbor])

def ucs_steps(start, goal):
    pq = [(0, [start])]
    visited = set()
    while pq:
        cost, path = heapq.heappop(pq)
        node = path[-1]
        yield node, path, cost
        if node == goal:
            return
        if node not in visited:
            visited.add(node)
            for neighbor, w in graph[node]:
                heapq.heappush(pq, (cost + w, path + [neighbor]))

def dls_steps(start, goal, limit):
    found = [False]
    def recursive_dls(path, depth):
        if found[0]:
            return
        node = path[-1]
        yield node, path, depth
        if node == goal:
            found[0] = True
            return
        if depth >= limit:
            return
        for neighbor, _ in graph[node]:
            if neighbor not in path:
                yield from recursive_dls(path + [neighbor], depth + 1)
    yield from recursive_dls([start], 0)

def ids_steps(start, goal, max_depth):
    found = False
    for depth in range(max_depth + 1):
        if found:
            return
        yield f"IDS: Depth {depth}"
        for node, path, d in dls_steps(start, goal, depth):
            yield node, path, d
            if node == goal:
                found = True
                return

# ---------------- GUI ----------------
class SearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QUIMA - Uninformed Search Visualization")
        self.root.geometry("1000x700")
        self.root.configure(bg="blue")

        top = tk.Frame(root, bg="blue")
        top.pack(pady=10)

        algorithms = [
            "BFS (Breadth-First Search)",
            "DFS (Depth-First Search)",
            "UCS (Uniform Cost Search)",
            "DLS (Depth-Limited Search)",
            "IDS (Iterative Deepening Search)"
        ]

        tk.Label(top, text="Algorithm:", bg="white", fg="blue", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5)
        self.algo_var = tk.StringVar(value=algorithms[0])
        self.algo_menu = ttk.Combobox(top, textvariable=self.algo_var, values=algorithms, state="readonly", width=32)
        self.algo_menu.grid(row=0, column=1, padx=5)
        self.algo_menu.bind("<<ComboboxSelected>>", self.toggle_limit_entry)

        tk.Label(top, text="Start:", bg="black", fg="white", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=5)
        self.start_entry = tk.Entry(top, width=5, font=("Arial", 11))
        self.start_entry.insert(0, "A")
        self.start_entry.grid(row=0, column=3, padx=5)

        tk.Label(top, text="Goal:", bg="black", fg="white", font=("Arial", 11, "bold")).grid(row=0, column=4, padx=5)
        self.goal_entry = tk.Entry(top, width=5, font=("Arial", 11))
        self.goal_entry.insert(0, "O")
        self.goal_entry.grid(row=0, column=5, padx=5)

        self.limit_label = tk.Label(top, text="Limit:", bg="black", fg="white", font=("Arial", 11, "bold"))
        self.limit_entry = tk.Entry(top, width=5, font=("Arial", 11))

        self.run_button = tk.Button(top, text="Run", command=self.run_search, bg="#590cf3", fg="black", font=("Arial", 10, "bold"))
        self.run_button.grid(row=0, column=6, padx=5)
        self.reset_button = tk.Button(top, text="Reset", command=self.reset_search, bg="#7709e4", fg="black", font=("Arial", 10, "bold"))
        self.reset_button.grid(row=0, column=7, padx=5)

        self.canvas = tk.Canvas(root, width=900, height=500, bg="light blue", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.result_label = tk.Label(root, text="", bg="black", fg="white", font=("Consolas", 12), wraplength=850, justify="left")
        self.result_label.pack(pady=10)

        self.draw_graph()
        self.toggle_limit_entry(None)

    def toggle_limit_entry(self, event):
        algo = self.algo_var.get()
        if "DLS" in algo or "IDS" in algo:
            self.limit_label.grid(row=0, column=8, padx=5)
            self.limit_entry.grid(row=0, column=9, padx=5)
        else:
            self.limit_label.grid_forget()
            self.limit_entry.grid_forget()

    def reset_search(self):
        self.draw_graph()
        self.result_label.config(text="")
        self.run_button.config(state=tk.NORMAL)

    def draw_graph(self):
        self.canvas.delete("all")
        for node, neighbors in directed_graph.items():
            x1, y1 = node_positions[node]
            for neighbor, weight in neighbors:
                x2, y2 = node_positions[neighbor]
                self.canvas.create_line(x1, y1, x2, y2, fill="gray30")
                self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text=str(weight), fill="yellow", font=("Arial", 8, "bold"))
        for node, (x, y) in node_positions.items():
            self.canvas.create_oval(x-12, y-12, x+12, y+12, fill="#ee03de", outline="white")
            self.canvas.create_text(x, y, text=node, fill="black", font=("Arial", 10, "bold"))

    def highlight_node(self, node, color, sleep=0.15):
        x, y = node_positions[node]
        self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=color, outline="white")
        self.canvas.create_text(x, y, text=node, fill="black", font=("Arial", 10, "bold"))
        self.root.update()
        time.sleep(sleep)

    def draw_exploration_order(self, order):
        for i in range(len(order)-1):
            n1, n2 = order[i], order[i+1]
            x1, y1 = node_positions[n1]
            x2, y2 = node_positions[n2]
            self.canvas.create_line(x1, y1, x2, y2, fill="#f8071b", width=2, dash=(6,4), arrow="last")

    def highlight_path_red(self, path):
        for i in range(len(path)-1):
            n1, n2 = path[i], path[i+1]
            x1, y1 = node_positions[n1]
            x2, y2 = node_positions[n2]
            self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)
        for node in path:
            self.highlight_node(node, "blue", sleep=0.1)

    def run_search(self):
        self.run_button.config(state=tk.DISABLED)
        self.draw_graph()
        self.result_label.config(text="")

        start = self.start_entry.get().strip().upper()
        goal = self.goal_entry.get().strip().upper()
        algo = self.algo_var.get()

        if start not in graph or goal not in graph:
            messagebox.showerror("Error", "Invalid start/goal node.")
            self.run_button.config(state=tk.NORMAL)
            return
        if start == goal:
            messagebox.showerror("Error", "Start and Goal cannot be the same.")
            self.run_button.config(state=tk.NORMAL)
            return

        limit = None
        if "DLS" in algo or "IDS" in algo:
            try:
                limit = int(self.limit_entry.get().strip())
            except:
                messagebox.showerror("Error", "Enter a valid numeric limit.")
                self.run_button.config(state=tk.NORMAL)
                return

        if "BFS" in algo: gen = bfs_steps(start, goal)
        elif "DFS" in algo: gen = dfs_steps(start, goal)
        elif "UCS" in algo: gen = ucs_steps(start, goal)
        elif "DLS" in algo: gen = dls_steps(start, goal, limit)
        elif "IDS" in algo: gen = ids_steps(start, goal, limit)
        else: return

        visited_nodes, path_found, total_cost = [], None, 0
        for step in gen:
            if isinstance(step, str):
                self.result_label.config(text=step)
                self.root.update()
                continue
            if "UCS" in algo:
                node, path, total_cost = step
            elif "DLS" in algo or "IDS" in algo:
                node, path, depth = step
            else:
                node, path = step
            visited_nodes.append(node)
            self.highlight_node(node, "lime")
            if node == goal:
                path_found = path
                break

        self.draw_exploration_order(visited_nodes)
        if path_found:
            text = f"Exploration Order: {' → '.join(visited_nodes)}"
            if "UCS" in algo:
                text += f"\nShortest Path: {' → '.join(path_found)}\nCost: {total_cost}"
                self.highlight_path_red(path_found)
            else:
                self.highlight_node(goal, "blue")
                if "DLS" in algo: text += f"\nDepth Limit = {limit}"
                if "IDS" in algo: text += f"\nMax Depth = {limit}"
            self.result_label.config(text=text)
        else:
            self.result_label.config(text="No path found within limit.")
        self.run_button.config(state=tk.NORMAL)

# ---------------- Run ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SearchGUI(root)
    root.mainloop()