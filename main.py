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

        self.setup_ui()
        self.bind_canvas_events()
        self.update_button_colors()
    
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
    
    def _color_vertex(self, x, y):
        vertex = self.find_vertex_by_position(x, y)
        ask = simpledialog.askstring("Color Vertex", f"Choose color:")
        neighbors = self.graph.get_neighbors(vertex)
        for neighbor in neighbors:
            if ask in neighbor.labels:
                return messagebox.askretrycancel("Miscoloring", "Seems like that vertex is already colored that!")
        vertex.add_label(ask)
    
    def _label_vertex(self, x, y):
        vertex = self.find_vertex_by_position(x, y)
        ask = simpledialog.askinteger("Label Vertex", f"Label Vertex:")
        vertex.add_label(ask)
    
    def _delete_vertex(self, x, y):
        vertex = self.find_vertex_by_position(x, y)
        if vertex:
            self.graph.remove_vertex(vertex)
        else:
            ask = messagebox.askyesno("Delete Graph", "Delete the Entire Graph?")
            if ask:
                self.graph.clear()
    
    def _line_graph(self):
        ask = messagebox.askokcancel("Line Graph", "Perform Line Graph?")
        if ask:
            self.graph.line_graph()
        self.update_edges()
    
    # External
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
            self.selected_vertex.selected = False

        vertex_label = self.find_vertex_by_position(x, y)
        if vertex_label:
            self.selected_vertex = vertex_label
            vertex_label.selected = True
        else:
            self.selected_vertex = None

    def set_state(self, state):
        self.current_state = state
        self.update_button_colors()

    def bind_canvas_events(self):
        def on_canvas_click(event):
            for state, data in self.states.items():
                if self.current_state == state:
                    data['method'](event.x, event.y)
            self.update_edges()
        def on_canvas_drag(event):
            if self.current_state == 'move_vertex' and self.selected_vertex:
                self._move_vertex(event.x, event.y)
            self.update_edges()
        self.canvas.bind("<Button-1>", on_canvas_click)
        self.canvas.bind("<B1-Motion>", on_canvas_drag)

    # UI Methods
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(main_frame, width=500, height=400, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=4, pady=(0, 10))

        self.states = {
            'add_vertex': {
                'name': "Add Vertex",
                'method': self._add_vertex,
                'element': tk.Button(self.root, command=lambda: self.set_state('add_vertex'))
            },
            'add_edge': {
                'name': "Add Edge",
                'method': self._start_edge,
                'element': tk.Button(self.root, command=lambda: self.set_state('add_edge'))
            },
            'move_vertex': {
                'name': "Move Vertex",
                'method': self.select_vertex,
                'element': tk.Button(self.root, command=lambda: self.set_state('move_vertex'))
            },
            'color_vertex': {
                'name': "Color Vertex",
                'method': self._color_vertex,
                'element': tk.Button(self.root, command=lambda: self.set_state('color_vertex'))
            },
            'delete': {
                'name': "Delete",
                'method': self._delete_vertex,
                'element': tk.Button(self.root, command=lambda: self.set_state('delete'))
            },
        }
        for data in self.states.values():
            data['element'].config(text=data['name'])
            data['element'].pack()

        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.grid(row=1, column=0, columnspan=4, pady=(10, 0))

        self.distance_distribution = tk.Button(
            button_frame, text="Distance Distribution",
            command=lambda: self.show_solution_box(f"The Distance Distribution is: {self.graph.distance_distribution(self.selected_vertex)}"),
            bg='lightblue'
        )
        self.line_graph_button = tk.Button(button_frame, text="Line Graph", command=self._line_graph, bg='lightblue')
        self.export_graph = tk.Button(button_frame, bg="lightgreen", text="Export Graph", command=self.export_new_graph)
        self.import_graph = tk.Button(button_frame, bg="lightgreen", text="Import Graph", command=self.import_new_graph)
        self.bfs_algo_button = tk.Button(button_frame, bg='lightyellow', text="BFS Algorithm", command=lambda: self.graph.label_by_bfs(self.selected_vertex))

        self.distance_distribution.grid(row=0, column=0, padx=5, pady=5)
        self.line_graph_button.grid(row=0, column=1, padx=5, pady=5)
        self.import_graph.grid(row=0, column=2, padx=5, pady=5)
        self.export_graph.grid(row=0, column=3, padx=5, pady=5)
        self.bfs_algo_button.grid(row=1, column=0, padx=5, pady=5)
    
    def update_button_colors(self):
        for state, data in self.states.items():
            if state == 'delete':
                data['element'].config(bg='grey' if self.current_state == state else 'red')
            else:
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
            return messagebox.showerror("Error", f"Graph with name {filename} doesn't exist!")
        
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
