import numpy as np

class Graph:
    def __init__(self):
        self.graph = {}

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []

    def add_edge(self, node1, node2):
        self.add_vertex(node1)
        self.add_vertex(node2)
        self.graph[node1].append(node2)
        self.graph[node2].append(node1)

    def get_vertices(self):
        return list(self.graph.keys())

    def get_edges(self):
        edges = []
        for vertex, neighbors in self.graph.items():
            for neighbor in neighbors:
                if (vertex, neighbor) not in edges and (neighbor, vertex) not in edges:
                    edges.append((vertex, neighbor))
        return edges

    def __str__(self):
        result = ""
        for node, neighbors in self.graph.items():
            result += f"{node}: {', '.join(map(str, neighbors))}\n"
        return result

    """ edges = double_list[[x, y]]"""
    def edge_list(self, edges):
        for e in edges:
            self.add_edge(e[0], e[1])
        return self

    def cycle(self, n):
        for num in range(0, n):
            self.add_edge(num, num + 1)
        self.add_edge(n+1, 0)
        return self

    def complete(self, n):
        for v1 in range(0, n):
            for v2 in range(0, n):
                if v2 > v1:
                    self.add_edge(v1, v2)
        return self

    def neighbors(self, vertex):
        neighbors = []
        if vertex in self.get_vertices():
            edges = self.get_edges()
            for edge in edges:
                if vertex in edge:
                    neighbors.append(edge[0] if edge[0] != vertex else edge[1])
        return neighbors

    def degree(self, vertex):
        return len(self.neighbors(vertex))

    def distance_distribution(self, vertex):
        vertices = self.get_vertices()
        used_vertices = [vertex, ]
        poly_add = [[vertex], ]
        distance = 0

        while len(used_vertices) < len(vertices):
            use = []
            for vert in poly_add[distance]:
                neighborhood = self.neighbors(vert)
                for n in neighborhood:
                    if n not in used_vertices:
                        used_vertices.append(n)
                        use.append(n)
            poly_add.append(use)
            distance += 1

        return poly_add

    def distance(self, v1, v2):
        distance = 0
        distribute = self.distance_distribution(v1)
        while v2 not in distribute[distance]:
            distance += 1
        return distance

    def distance_polynomial(self, vertex):
        distribute = self.distance_distribution(vertex)
        polynomial = []
        for dist in distribute:
            polynomial.append(len(dist))
        return polynomial

    def adjacency_matrix(self):
        vertices = self.get_vertices()
        edges = self.get_edges()
        matrix = []
        for h in range(len(vertices)):
            matrix.append([])
            for v in range(len(vertices)):
                if (vertices[h], vertices[v]) in edges or (vertices[v], vertices[h]) in edges:
                    matrix[h].append(1)
                else:
                    matrix[h].append(0)
        return np.array(matrix)

    def degree_matrix(self):
        vertices = self.get_vertices()
        degrees = []
        for v in vertices:
            degrees.append(self.degree(v))
        return np.diag(degrees)

    def laplacian_matrix(self):
        return self.degree_matrix() - self.adjacency_matrix()

    def distance_matrix(self):
        vertices = self.get_vertices()
        matrix = []
        for h in range(len(vertices)):
            matrix.append([])
            for v in range(len(vertices)):
                matrix[h].append(self.distance(h, v))
        return np.array(matrix)


# Example usage:
petersen = [[1,2],[2,3],[3,4],[4,5],[5,1],[1,6],[2,7],[3,8],[4,9],[5,10],[6,8],[7,9],[8,10],[9,6],[10,7]]
heawood = [[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10],[10,11],[11,12],[12,13],[13,14],[14,1],
           [1,6],[3,8],[5,10],[7,12],[9,14],[11,2],[13,4]]


pet = Graph().edge_list(petersen)
hea = Graph().edge_list(heawood)
pet_adj = pet.adjacency_matrix()
pet_deg = pet.degree_matrix()
pet_lap = pet.laplacian_matrix()

square = Graph().cycle(4)
print(square.distance_matrix())

print(pet_adj)
print(pet_deg)
print(pet_lap)
print(pet.distance_polynomial(1))
print(pet.distance_distribution(1))
