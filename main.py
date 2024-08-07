import tkinter as tk
from tkinter import messagebox, simpledialog
from backend.definitions import Graph, Vertex
from backend.utils import generate_random_id


class GraphBuilder:
    def __init__(self, root):
        self.root = root
        self.graph = Graph("Graphematics")
        self.root.title(self.graph.name)

        self.current_state = 'add_vertex'
        self.selected_vertex = None
        
        self.add_vertex_button = tk.Button(self.root, text="Add Vertex", command=lambda: self.set_state('add_vertex'))
        self.add_edge_button = tk.Button(self.root, text="Add Edge", command=lambda: self.set_state('add_edge'))
        self.move_vertex_button = tk.Button(self.root, text="Move Vertex", command=lambda: self.set_state('move_vertex'))
        self.color_vertex_button = tk.Button(self.root, text="Color Vertex", command=lambda: self.set_state('color_vertex'))
        self.delete_button = tk.Button(self.root, text="Delete", command=lambda: self.set_state('delete'))
        self.states = {
            'add_vertex': {
                'name': "Add Vertex",
                'method': self._add_vertex,
                'element': self.add_vertex_button
            },
            'add_edge': {
                'name': "Add Edge",
                'method': self._start_edge,
                'element': self.add_edge_button
            },
            'move_vertex': {
                'name': "Move Vertex",
                'method': self.select_vertex,
                'element': self.move_vertex_button
            },
            'color_vertex': {
                'name': "Label Vertex",
                'method': self._color_vertex,
                'element': self.color_vertex_button
            },
            'delete': {
                'name': "Delete",
                'method': self._delete_vertex,
                'element': self.delete_button
            },
        }

        self.setup_ui()
        self.bind_canvas_events()
    
    # State Functions
    def _add_vertex(self, x, y):
        vertex_id = generate_random_id()
        if vertex_id and vertex_id not in self.graph.vertices:
            vertex = Vertex(self.canvas, x, y, id=vertex_id)
            self.graph.create_vertex(vertex)

    def _start_edge(self, x, y):
        vertex_label = self.find_vertex_by_position(x, y)
        if vertex_label:
            if not hasattr(self, 'edge_start'):
                self.edge_start = vertex_label
                self.select_vertex(x, y)
            else:
                self.graph.create_edge(self.edge_start, vertex_label)
                self.draw_edge(self.edge_start, vertex_label)
                del self.edge_start
                self.select_vertex(0, 0)

    def _move_vertex(self, x, y):
        if self.selected_vertex:
            self.selected_vertex.update_position(x, y)
            self.update_edges()
    
    def _color_vertex(self, x, y):
        vertex = self.find_vertex_by_position(x, y)
        ask = simpledialog.askstring("Label Vertex", f"Choose color:")
        neighbors = self.graph.get_neighbors(vertex)
        for neighbor in neighbors:
            if ask in neighbor.labels:
                return messagebox.askretrycancel("Miscoloring", "Seems like that vertex is already colored that!")
        vertex.add_label(ask)
        self.update_edges()
    
    def _delete_vertex(self, x, y):
        vertex = self.find_vertex_by_position(x, y)
        self.graph.remove_vertex(vertex)
        self.update_edges()
    
    # External   
    def setup_ui(self):
        self.canvas = tk.Canvas(self.root, width=500, height=400, bg='white')
        self.canvas.pack()

        for data in self.states.values():
            data['element'].pack()
        
        self.distance_distribution = tk.Button(
            self.root, text="Distance Distribution",
            command=lambda: self.show_solution_box(f"The Distance Distribution is: {self.graph.distance_distribution(self.selected_vertex)}")
        )
        self.distance_distribution.pack()
        self.line_graph_button = tk.Button(self.root, text="Line Graph", command=self._line_graph)
        self.export_graph = tk.Button(self.root, bg="pink", text="Export Graph", command=self.export_new_graph)
        self.import_graph = tk.Button(self.root, bg="pink",text="Import Graph", command=self.import_new_graph)
        self.line_graph_button.pack()
        self.import_graph.pack()
        self.export_graph.pack()
        self.update_button_colors()

    def _line_graph(self):
        ask = messagebox.askokcancel("Line Graph", "Perform Line Graph?")
        if ask:
            self.graph.line_graph()
            self.update_edges()

    def find_vertex(self, x, y, radius=10):
        for vertex in self.graph.vertices:
            if (vertex.x - radius <= x <= vertex.x + radius) and (vertex.y - radius <= y <= vertex.y + radius):
                return vertex
        return None
    
    def find_vertex_by_position(self, x, y):
        for vertex in self.graph.vertices:
            if vertex.contains_point(x, y):
                return vertex
        return None
    
    def select_vertex(self, x, y):
        if self.selected_vertex:
            self.selected_vertex.set_selected(False)

        vertex_label = self.find_vertex_by_position(x, y)
        if vertex_label:
            self.selected_vertex = vertex_label
            vertex_label.set_selected(True)
        else:
            self.selected_vertex = None

    def set_state(self, state):
        self.current_state = state
        self.update_button_colors()

    def bind_canvas_events(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
    def on_canvas_click(self, event):
        for state, data in self.states.items():
            if self.current_state == state:
                data['method'](event.x, event.y)
    def on_canvas_drag(self, event):
        if self.current_state == 'move_vertex' and self.selected_vertex:
            self._move_vertex(event.x, event.y)

    # UI Methods
    def update_button_colors(self):
        for state, data in self.states.items():
            data['element'].config(bg='grey' if self.current_state == state else 'white')

    def draw_edge(self, start_vertex, end_vertex):
        x1, y1 = start_vertex.x, start_vertex.y
        x2, y2 = end_vertex.x, end_vertex.y
        self.canvas.create_line(x1, y1, x2, y2, fill='black')

    def update_edges(self):
        self.canvas.delete("all")
        for vertex in self.graph.vertices:
            vertex.vertex_id = vertex.draw_vertex()
            vertex.update_labels()
        for start_label, end_labels in self.graph.edges.items():
            start_vertex = self.graph.get_vertex_by_id(start_label)
            if not start_vertex:
                raise ValueError(f"Start vertex {start_label} isn't in the graph.")
            
            for end_label in end_labels:
                end_vertex = self.graph.get_vertex_by_id(end_label)
                if not end_vertex:
                    raise ValueError(f"End vertex {end_label} isn't in the graph.")
                
                self.draw_edge(start_vertex, end_vertex)
    
    # Box Methods
    def show_solution_box(self, text):
        messagebox.showinfo("Info", text)

    def export_new_graph(self):
        text = simpledialog.askstring("Export Graph", "Name your Graph:")
        self.graph.name = text
        self.graph.export_graph_data(filename=text)
    
    def import_new_graph(self):
        filename = simpledialog.askstring("Import Graph", "Search Graph by Name:")
        if not filename:
            return None
        
        for class_name, class_val in self.graph.classes.items():
            self.graph.clear()
            if filename == class_name:
                name = class_val["name"]
                params = class_val["params"]
                func = class_val["function"]
                func_params = []
                for param in params:
                    ask = simpledialog.askinteger(name, f"Choose {param}:")
                    func_params.append(ask)
                func(self.canvas, *func_params)
                self.update_edges()
                return None
            
        self.graph.import_graph_data(filename, self.canvas)
        self.update_edges()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphBuilder(root)
    root.mainloop()
