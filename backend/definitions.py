from backend.utils import generate_random_id

class Vertex:
    def __init__(self, canvas, x, y, id=generate_random_id(), radius=10, color='blue'):
        self.canvas = canvas
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        self.vertex_id = self.draw_vertex()

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
    
    def get_vertex_by_id(self, id: str) -> Vertex:
        for vertex in self.vertices:
            if vertex.id == id:
                return vertex
        return None
    
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
    
    def save(self):
        with open("database.txt", 'w') as file:
            file.write(self.__repr__())
    
    def import_graph_data(self, data: dict, canvas):
        """
            data = {
                'vertex_id': {
                    'neighbors': [vertices],
                    'position': (x, y)
                }
            }
        """
        self.clear()
        for vertex_id, vertex_data in data.items():
            self.edges[vertex_id] = vertex_data['neighbors']
            vertex = Vertex(canvas, *vertex_data['position'], id=vertex_id)
            self.vertices.append(vertex)

    def export_graph_data(self):
        data = {}
        for vertex in self.vertices:
            vertex_data = {}
            vertex_data['neighbors'] = self.edges[vertex.id]
            vertex_data['position'] = (vertex.x, vertex.y)
            data[vertex.id] = vertex_data
        return data

    def __repr__(self):
        return f"{self.name}:\nVertices: {self.vertices}\nEdges: {self.edges}\n"
