from collections import deque
import numpy as np
import json
import random
import string
import os
import math
from itertools import permutations


def generate_random_id(length=8):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choices(characters, k=length))
    return random_id


def get_data_path(filename):
    directory = './storage'
    unique_filename = f"{filename}.json"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, unique_filename)

def int_to_color(integer):
    colorize = {
        "0": "blue",
        "1": "red",
        "2": "green",
        "3": "yellow",
        "4": "purple",
        "5": "orange",
        "6": "pink",
        "7": "brown",
        "8": "gray",
        "9": "cyan"
    }
    return colorize.get(str(integer%10), "black")

class Vertex:
    def __init__(self, canvas, x, y, id=None, radius=10, color='black', labels=[]):
        self.canvas = canvas
        self.id = id if id else generate_random_id()
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.selected = False

        self.vertex_id = self.draw_vertex()
        self.labels = labels

    def draw_vertex(self):
        return self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=self.color
        )
    
    def draw_int_label(self, label: int, color='white'):
        self.canvas.create_text(
            self.x, self.y,
            text=label, fill=color
        )

    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.canvas.coords(
            self.vertex_id, self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius
        )
        self.canvas.coords(self.x, self.y)

    def update_color(self, color):
        self.canvas.itemconfig(self.vertex_id, fill=color)
        self.color = color

    def contains_point(self, x, y):
        return (self.x - self.radius <= x <= self.x + self.radius) and (self.y - self.radius <= y <= self.y + self.radius)

    def set_selected(self):
        if self.selected:
            self.canvas.itemconfig(self.vertex_id, outline='red', width=3)
        else:
            self.canvas.itemconfig(self.vertex_id, outline='black', width=1)

    def add_label(self, label, overwrite=True):
        if overwrite:
            self.labels = []
        self.labels.append(label)
        self.update_labels()
    
    def update_labels(self):
        for label in self.labels:
            try:
                self.update_color(label)
            except Exception:
                self.draw_int_label(label)
    
    def get_position(self):
        return (self.x, self.y)


class Graph:
    def __init__(self, name, simple=True, directed=False):
        self.name = name
        self.vertices = []
        self.edges = {}
        self.simple = simple
        self.directed = directed

        self.classes = {
            "cyclic": {
                "name": "Cyclic Graph",
                "params": ["number of nodes"],
                "function": self._cyclic_graph
            },
            "genpet": {
                "name": "Generalized Petersen Graph",
                "params": ["parameter 1", "parameter 2"],
                "function": self._generalized_petersen_graph
            },
            "complete": {
                "name": "Complete Graph",
                "params": ["number of nodes"],
                "function": self._complete_graph
            },
            "wheel": {
                "name": "Wheel Graph",
                "params": ["outer node number"],
                "function": self._wheel_graph
            },
            "bicomplete": {
                "name": "Bipartite Complete Graph",
                "params": ["parameter 1", "parameter 2"],
                "function": self._complete_bipartite_graph
            },
        }
    
    def __str__(self):
        return f"{self.name}:\nVertices: {self.vertices}\nEdges: {self.edges}\n"
    
    def get_vertex_by_id(self, id: str) -> Vertex:
        for vertex in self.vertices:
            if vertex.id == id:
                return vertex
        return None
    def get_vertex_by_label(self, label) -> Vertex:
        for vertex in self.vertices:
            if label in vertex.labels:
                return vertex
        return None
    def get_vertices_by_label(self, label) -> Vertex:
        vertices = []
        for vertex in self.vertices:
            if label in vertex.labels:
                vertices.append(vertex)
        return vertices
    def get_neighbors(self, vertex: Vertex):
        neighbors = []
        for neighbor_id in self.edges[vertex.id]:
            neighbor = self.get_vertex_by_id(neighbor_id)
            neighbors.append(neighbor)
        return neighbors
    
    def remove_all_labels(self):
        for vertex in self.vertices:
            vertex.labels = []
    
    def create_vertex(self, vertex: Vertex):
        if vertex.id in self.vertices:
            raise ValueError(f"Vertex with id '{vertex.id}' already exists.")
        self.vertices.append(vertex)
        self.edges[vertex.id] = []
    def remove_vertex(self, vertex: Vertex):
        if vertex not in self.vertices:
            raise ValueError(f"Vertex with label '{vertex.id}' doesn't exist.")
        self.vertices.remove(vertex)
        for connected_vertices in self.edges.values():
            if vertex.id in connected_vertices:
                connected_vertices.remove(vertex.id)
        del self.edges[vertex.id]
            

    def create_edge(self, v1: Vertex, v2: Vertex):
        if v1 not in self.vertices or v2 not in self.vertices:
            raise ValueError("Both vertices must be in the graph")
        if self.simple:
            if v2.id in self.edges[v1.id] or v1.id in self.edges[v2.id]:
                return ValueError("Edge already exists in graph.")
            if v1 == v2:
                raise ValueError("Vertex can not share the same vertex.")
        self.edges[v1.id].append(v2.id)
        if not self.directed:
            self.edges[v2.id].append(v1.id)
    def remove_edge(self, v1, v2):
        if v1 in self.vertices and v2 in self.vertices:
            if v2 in self.edges[v1.id]:
                self.edges[v1.id].remove(v2.id)
            if v1 in self.edges[v2.id]:
                self.edges[v2.id].remove(v1.id)
        else:
            raise ValueError("Both vertices must be in the graph")
    
    def degrees(self):
        return [len(neighbors) for neighbors in self.edges.values()]
    
    def clear(self):
        self.vertices = []
        self.edges = {}
    
    def import_graph_data(self, filename, canvas):
        """
            data = {
                'vertex_id': {
                    'neighbors': [vertices],
                    'position': (x, y),
                    'labels': [any]
                }
            }
        """
        self.clear()
        self.name = filename
        path = get_data_path(filename)
        with open(path, 'r') as graph_data:
            data = json.load(graph_data)
        
        for vertex_id, vertex_data in data.items():
            self.edges[vertex_id] = vertex_data['neighbors']
            vertex = Vertex(canvas, *vertex_data['position'], id=vertex_id, labels=vertex_data['labels'])
            self.vertices.append(vertex)

    def export_graph_data(self, filename='graph_data'):
        if filename in self.classes.keys():
            raise NameError("Graph can not be named this!")
        
        data = {}
        for vertex in self.vertices:
            vertex_data = {}
            vertex_data['neighbors'] = self.edges[vertex.id]
            vertex_data['position'] = (vertex.x, vertex.y)
            vertex_data['labels'] = vertex.labels
            data[vertex.id] = vertex_data
        
        path = get_data_path(filename)
        with open(os.path.join(path), 'w') as graph_file:
            json.dump(data, graph_file, indent=4)
        return data
    

    # Graph Classes
    def _cyclic_graph(self, canvas, nodes, radius=100, bump=0, remove_labels=True, star=1):
        center = (canvas.winfo_width() / 2, canvas.winfo_height() / 2)
        angle_increment = 2 * math.pi / nodes
        for i in range(nodes):
            location = (center[0] + radius * math.cos(i * angle_increment), center[1] + radius * math.sin(i * angle_increment))
            vertex = Vertex(canvas, *location, labels=[bump + i])
            self.create_vertex(vertex)
        
        for i in range(nodes):
            self.create_edge(self.get_vertex_by_label(bump + i%nodes), self.get_vertex_by_label(bump+ (i + star)%nodes))

        if remove_labels:
            self.remove_all_labels()

    def _generalized_petersen_graph(self, canvas, outer, star):
        self._cyclic_graph(canvas, outer, radius =50, remove_labels=False, star=star)
        self._cyclic_graph(canvas, outer, bump=outer, remove_labels=False)
        for i in range(outer):
            vertex1 = self.get_vertex_by_label(i)
            vertex2 = self.get_vertex_by_label(outer + i)
            self.create_edge(vertex1, vertex2)
        self.remove_all_labels()

    def _wheel_graph(self, canvas, n):
        center = (canvas.winfo_width() / 2, canvas.winfo_height() / 2)
        self._cyclic_graph(canvas, n)
        center_vertex = Vertex(canvas, *center, labels=["center"])
        self.create_vertex(center_vertex)
        for v in self.vertices:
            if "center" not in v.labels:
                self.create_edge(center_vertex, v)
        self.remove_all_labels()
    
    def _complete_graph(self, canvas, nodes, radius=100, remove_labels=True):
        center = (canvas.winfo_width() / 2, canvas.winfo_height() / 2)
        angle_increment = 2 * math.pi / nodes
        for i in range(nodes):
            location = (center[0] + radius * math.cos(i * angle_increment), center[1] + radius * math.sin(i * angle_increment))
            vertex = Vertex(canvas, *location, labels=[i])
            self.create_vertex(vertex)
        for v1 in self.vertices:
            for v2 in self.vertices:
                if v1.labels[0] < v2.labels[0]:
                    self.create_edge(v1, v2)
        if remove_labels:
            self.remove_all_labels()
    
    def _complete_bipartite_graph(self, canvas, nodes1, nodes2, gap=100):
        width = canvas.winfo_width()
        middle = canvas.winfo_height()/2
        tops = []
        bottoms = []
        for i in range(nodes1 + nodes2):
            if i < nodes1:
                x = i * (width/(nodes1 + 1)) + (width/(nodes1 + 1))
                y = middle + gap/2
                vertex = Vertex(canvas, x, y)
                self.create_vertex(vertex)
                tops.append(vertex)
            else:
                x = (i - nodes1) * (width/(nodes2 + 1)) + (width/(nodes2 + 1))
                y = middle - gap/2
                vertex = Vertex(canvas, x, y)
                self.create_vertex(vertex)
                bottoms.append(vertex)
        for vertex1 in tops:
            for vertex2 in bottoms:
                self.create_edge(vertex1, vertex2)


    # Graph Functions
    def line_graph(self):
        old_edges = list(self.edges.items())
        for vertex_id, neighbors in old_edges:
            vertex = self.get_vertex_by_id(vertex_id)
            for neighbor in neighbors:
                neighbor = self.get_vertex_by_id(neighbor)
                midpoint = ((vertex.x + neighbor.x)/2, (vertex.y + neighbor.y)/2)
                add_vertex = Vertex(vertex.canvas, *midpoint, labels=[vertex.id, neighbor.id])
                self.create_vertex(add_vertex)
            self.remove_vertex(vertex)
        for vertex in self.vertices:
            neighbors = self.get_vertices_by_label(vertex.labels[0])
            neighbors.extend(self.get_vertices_by_label(vertex.labels[1]))
            for neighbor in neighbors:
                try:
                    self.create_edge(vertex, neighbor)
                except ValueError:
                    continue
        self.remove_all_labels()
    
    def label_by_bfs(self, vertex: Vertex, colorize=True):
        set_labels = self.bfs_algorithm(vertex)
        for vert in self.vertices:
            label = int_to_color(set_labels[vert.id]) if colorize else set_labels[vert.id]
            vert.add_label(label, overwrite=False)


    # Important Functions
    def bfs_algorithm(self, start_vertex: Vertex):
        if start_vertex.id not in self.edges:
            raise ValueError("Vertex must be in the graph")
        distances = {vertex.id: float('inf') for vertex in self.vertices}
        distances[start_vertex.id] = 0
        queue = deque([start_vertex.id])
        while queue:
            current_id = queue.popleft()
            current_distance = distances[current_id]
            for neighbor_id in self.edges[current_id]:
                if distances[neighbor_id] == float('inf'):
                    distances[neighbor_id] = current_distance + 1
                    queue.append(neighbor_id)
        return distances

    def distance_distribution(self, vertex: Vertex):
        if vertex.id not in self.edges:
            raise ValueError("Vertex must be in the graph")
        distance = []
        distances = self.bfs_algorithm(vertex)
        distance.extend(d for d in distances.values() if d < float('inf'))
        if distance:
            max_distance = max(distance)
            distance_histogram, bins = np.histogram(distance, bins=range(max_distance + 2))
        else:
            distance_histogram = np.array([])
            bins = np.array([])
        return distance_histogram


class GraphIsomorphism:
    def __init__(self, name="", description=""):
        self.name = name
        self.description = description
        self.edges = {}

    def create_from_graph(self, graph: Graph):
        for vertex, neighbors in graph.edges.items():
            self.edges[vertex] = neighbors
        self.name = graph.name
    
    def check_isomorphism(self, graph: Graph):
        degrees = sorted([len(details.neighbors) for details in graph.edges.values()])
        iso_degrees = sorted([len(neighbors) for neighbors in self.edges.values()])
        if degrees != iso_degrees:
            return False
        
        vertices = self.edges.keys()
        for perm in permutations(graph.edges.keys()):
            mapping = dict(zip(vertices, perm))
            if all(
                set(self.edges[v1]) == set(mapping[v2] for v2 in graph.edges[mapping[v1]].neighbors)
                for v1 in vertices
            ):
                return True
        return False