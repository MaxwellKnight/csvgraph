import networkx as nx
import matplotlib.pyplot as plt

# Class representing a node in the graph
class CSVNode:
    def __init__(self, key: int, columns: list[str] = []):
        self.key = key
        self.columns = columns

    def __repr__(self) -> str:
        return f"{self.key}"

# Class representing an edge between two nodes in the graph
class CSVEdge:
    def __init__(self, left_v: CSVNode, right_v: CSVNode, columns: list[str]):
        self.left_v: CSVNode = left_v
        self.right_v: CSVNode = right_v
        self.column: list[str] = columns

    def __repr__(self) -> str:
        return f"({self.column}: {self.left_v.key} <--> {self.right_v.key})\n"

# Class representing the graph of CSV relationships
class CSVGraph:
    def __init__(self, nodes: list[CSVNode] = []):
        self.nodes: list[CSVNode] = nodes
        self.edges: list[CSVEdge] = []

    def add_edge(self, edge: CSVEdge):
        # Ensure consistent order of nodes in the edge
        if edge.left_v.key > edge.right_v.key:
            edge = CSVEdge(edge.right_v, edge.left_v, edge.column)

        for e in self.edges:
            if e.left_v == edge.left_v and e.right_v == edge.right_v and e.column == edge.column:
                return

        self.edges.append(edge)

    def __repr__(self):
        return '\n'.join([repr(edge) for edge in self.edges])

    def _extract_column_labels(self) -> set[str]:
        """Extract unique column labels from the graph's edges."""
        column_labels = set()
        for edge in self.edges:
            column_labels.update(edge.column)
        return column_labels

    def _find_reachable_nodes(self, start_node: CSVNode, column_label: str) -> list[CSVNode]:
        """Find nodes reachable from start_node using only edges with column_label."""
        visited = set()
        reachable_nodes = []

        def dfs(current_node):
            if current_node in visited:
                return
            visited.add(current_node)
            reachable_nodes.append(current_node)

            for edge in self.edges:
                if (current_node == edge.left_v or current_node == edge.right_v) and column_label in edge.column:
                    next_node = edge.right_v if current_node == edge.left_v else edge.left_v
                    dfs(next_node)

        dfs(start_node)
        return reachable_nodes

    def _create_direct_edges(self, column_label: str):
        """Create direct edges for all nodes reachable via column_label."""
        new_edges = []

        for node in self.nodes:
            reachable_nodes = self._find_reachable_nodes(node, column_label)
            for target_node in reachable_nodes:
                if node != target_node and not any(
                    (edge.left_v == node and edge.right_v == target_node or edge.left_v == target_node and edge.right_v == node) and column_label in edge.column
                    for edge in self.edges
                ):
                    new_edges.append(CSVEdge(node, target_node, [column_label]))

        self.edges.extend(new_edges)

    def compress_graph(self):
        """Compress paths for all columns while keeping the original edges."""
        column_labels = self._extract_column_labels()
        for column_label in column_labels:
            self._create_direct_edges(column_label)

    def find_path(self, src: CSVNode, dest: CSVNode):
        visited = set()
        queue = [(src, [src])] #stores the source node and it's path

        while queue:
            current, path = queue.pop(0)
            if current.key in visited: continue
            visited.add(current.key)

            # return the path if the destination is reached
            if current.key == dest.key: return path 

            for edge in self.edges:
                if edge.left_v.key == current.key:
                    queue.append((edge.right_v, path + [edge.right_v]))
                elif edge.right_v.key == current.key:
                    queue.append((edge.left_v, path + [edge.left_v]))

        #return None if there's no path between the source and the destination
        return None 

def visualize(graph):
    G = nx.Graph()

    for node in graph.nodes: G.add_node(node.key)

    for edge in graph.edges: G.add_edge(edge.left_v.key, edge.right_v.key, label=edge.column[0])

    pos = nx.spring_layout(G, k=10, seed=25)
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="skyblue", edgecolors="black")
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.6, edge_color="gray")
    nx.draw_networkx_labels(G, pos, labels={node: node for node in G.nodes}, font_size=10, font_weight="bold")

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=10)

    plt.title("Graph Visualization")
    plt.axis('off')
    plt.show()
