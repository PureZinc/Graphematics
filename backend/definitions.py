from collections import deque
import numpy as np
import json
import random
import time
import string
import os
import math


def generate_random_id(length=8):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choices(characters, k=length))
    return random_id

class Vertex:
    def __init__(self, canvas, x, y, id=None, radius=10, color='blue', label=None):
        self.canvas = canvas
        self.id = id if id else generate_random_id()
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        self.vertex_id = self.draw_vertex()
        self.label = label

    def draw_vertex(self):
        return self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=self.color
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
        self.color = color
        self.canvas.itemconfig(self.vertex_id, fill=self.color)

    def contains_point(self, x, y):
        return (self.x - self.radius <= x <= self.x + self.radius) and (self.y - self.radius <= y <= self.y + self.radius)

    def set_selected(self, selected):
        if selected:
            self.update_color('red')
        else:
            self.update_color('blue')


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
            if vertex.label == label:
                return vertex
        return None
    
    def remove_all_labels(self):
        for vertex in self.vertices:
            if vertex.label:
                vertex.label = None
    
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
            

    def create_edge(self, v1, v2):
        if v1 not in self.vertices or v2 not in self.vertices:
            raise ValueError("Both vertices must be in the graph")
        if self.simple:
            if v2.id in self.edges[v1.id] or v1.id in self.edges[v2.id]:
                raise ValueError("Edge already exists in graph.")
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
        
    def clear(self):
        self.vertices = []
        self.edges = {}
    
    def import_graph_data(self, filename, canvas):
        """
            data = {
                'vertex_id': {
                    'neighbors': [vertices],
                    'position': (x, y),
                    'label': any
                }
            }
        """
        self.clear()
        self.name = filename

        directory = './storage'
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, f'{filename}.json'), 'r') as graph_file:
            data = json.load(graph_file)

        for vertex_id, vertex_data in data.items():
            self.edges[vertex_id] = vertex_data['neighbors']
            vertex = Vertex(canvas, *vertex_data['position'], id=vertex_id)
            self.vertices.append(vertex)

    def export_graph_data(self, filename='graph_data'):
        if filename in self.classes.keys():
            raise NameError("Graph can not be named this!")
        
        data = {}
        for vertex in self.vertices:
            vertex_data = {}
            vertex_data['neighbors'] = self.edges[vertex.id]
            vertex_data['position'] = (vertex.x, vertex.y)
            data[vertex.id] = vertex_data
        
        timestamp = time.strftime("%Y%m%d-%H%M%S") #Use this for unique storage
        unique_filename = f'{filename}.json'
        directory = './storage'
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, unique_filename), 'w') as graph_file:
            json.dump(data, graph_file, indent=4)
        return data
    

    # Graph Classes
    def _cyclic_graph(self, canvas, nodes, radius=100, bump=0, remove_labels=True, star=1):
        center = (canvas.winfo_width() / 2, canvas.winfo_height() / 2)
        angle_increment = 2 * math.pi / nodes
        for i in range(nodes):
            location = (center[0] + radius * math.cos(i * angle_increment), center[1] + radius * math.sin(i * angle_increment))
            vertex = Vertex(canvas, *location, label=bump + i)
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
        center_vertex = Vertex(canvas, *center, label="center")
        self.create_vertex(center_vertex)
        for v in self.vertices:
            if v.label != "center":
                self.create_edge(center_vertex, v)
        self.remove_all_labels()
    
    def _complete_graph(self, canvas, nodes, radius=100, remove_labels=True):
        center = (canvas.winfo_width() / 2, canvas.winfo_height() / 2)
        angle_increment = 2 * math.pi / nodes
        for i in range(nodes):
            location = (center[0] + radius * math.cos(i * angle_increment), center[1] + radius * math.sin(i * angle_increment))
            vertex = Vertex(canvas, *location, label=i)
            self.create_vertex(vertex)
        for v1 in self.vertices:
            for v2 in self.vertices:
                if v1.label < v2.label:
                    self.create_edge(v1, v2)
        if remove_labels:
            self.remove_all_labels()


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
