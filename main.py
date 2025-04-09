import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict, deque

# Define graph structure
def create_graph():
    graph = {
        1: [(2, "U(3,5)"), (5, "6")],
        2: [(3, "6"), (4, "U(7,9)")],
        3: [(4, "U(5,8)")],
        4: [(7, "4")],
        5: [(3, "7"), (4, "9"), (6, "U(7,10)")],
        6: [(7, "U(8,12)")],
        7: []
    }
    return graph

# Parse time description, return specific time value
def get_time(time_desc):
    if time_desc.startswith("U"):
        # Extract parameters for uniform distribution
        params = time_desc[2:-1].split(",")
        lower = int(params[0])
        upper = int(params[1])
        return np.random.uniform(lower, upper)
    else:
        # Deterministic time
        return float(time_desc)

# Find all paths from start to end
def find_all_paths(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node, _ in graph[start]:
        if node not in path:
            new_paths = find_all_paths(graph, node, end, path)
            for new_path in new_paths:
                paths.append(new_path)
    return paths

# Simulate network execution, return time statistics for each path
def simulate_network(graph, num_simulations=10000):
    all_paths = find_all_paths(graph, 1, 7)
    path_times = defaultdict(list)
    
    critical_path_counts = defaultdict(int)
    
    for _ in range(num_simulations):
        # Calculate time for each path
        current_path_times = {}
        for path in all_paths:
            total_time = 0
            for i in range(len(path) - 1):
                current = path[i]
                next_node = path[i + 1]
                # Find time description for the edge
                for neighbor, time_desc in graph[current]:
                    if neighbor == next_node:
                        total_time += get_time(time_desc)
                        break
            
            path_key = "->".join(map(str, path))
            current_path_times[path_key] = total_time
            path_times[path_key].append(total_time)
        
        # Find critical path in current simulation
        critical_path = max(current_path_times.items(), key=lambda x: x[1])[0]
        critical_path_counts[critical_path] += 1
    
    # Calculate statistics for each path
    path_stats = {}
    for path_key, times in path_times.items():
        path_stats[path_key] = {
            "mean": np.mean(times),
            "std": np.std(times),
            "min": np.min(times),
            "max": np.max(times),
            "criticality": critical_path_counts[path_key] / num_simulations * 100
        }
    
    return path_stats, path_times

# Analyze system performance and visualize results
def analyze_system():
    graph = create_graph()
    stats, times = simulate_network(graph)
    
    print("Path Analysis Results:")
    for path, stat in sorted(stats.items(), key=lambda x: x[1]["mean"], reverse=True):
        print(f"Path {path}:")
        print(f"  Mean time: {stat['mean']:.2f}")
        print(f"  Standard deviation: {stat['std']:.2f}")
        print(f"  Min/Max time: {stat['min']:.2f}/{stat['max']:.2f}")
        print(f"  Critical path probability: {stat['criticality']:.2f}%")
        print()
    
    # Plot path time distributions
    plt.figure(figsize=(12, 8))
    for path, path_times in times.items():
        plt.hist(path_times, alpha=0.3, bins=30, label=path)
    
    y_max = plt.gca().get_ylim()[1]
    plt.ylim(0, y_max * 0.1)
    
    plt.title("Execution Time Distribution for Each Path")
    plt.xlabel("Execution Time")
    plt.ylabel("Frequency")
    plt.legend()
    plt.savefig("path_distributions.png")
    
    # Plot critical path probabilities
    plt.figure(figsize=(12, 6))
    paths = list(stats.keys())
    criticalities = [stats[path]["criticality"] for path in paths]
    
    plt.bar(paths, criticalities)
    plt.title("Probability of Each Path Being Critical")
    plt.xlabel("Path")
    plt.ylabel("Probability (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("path_criticality.png")
    
    return stats

if __name__ == "__main__":
    analyze_system()
