import tkinter as tk
from tkinter import messagebox, simpledialog
from backend.definitions import Graph, Vertex


class Graphematics:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphematics")
        self.graph = Graph("Graph1")

        self.current_state = 'add_vertex'

        self.init_widgets()
        self.layout_widgets()
        self.update_output()

    def init_widgets(self):
        self.vertex_label = tk.Label(self.root, text="Vertex Label:")
        self.vertex_entry = tk.Entry(self.root)
        self.add_vertex_button = tk.Button(self.root, text="Add Vertex", bg=self.add_vertex_color, command=lambda: self.set_state('add_vertex'))
        self.add_vertex_button.pack()

        self.add_edge_button = tk.Button(self.root, text="Add Edge", bg=self.add_edge_color, command=lambda: self.set_state('add_edge'))
        self.add_edge_button.pack()

        self.move_vertex_button = tk.Button(self.root, text="Move Vertex", bg=self.move_vertex_color, command=lambda: self.set_state('move_vertex'))
        self.move_vertex_button.pack()

        self.canvas = tk.Canvas(self.root, width=500, height=400, bg='white')

        self.import_button = tk.Button(self.root, text="Import Graph", bg="purple")
        self.save_button = tk.Button(self.root, text="Save Graph", bg="green", command=self.save)
        self.clear_button = tk.Button(self.root, text="Clear Graph", bg="red", command=self.clear)
    
    def layout_widgets(self):
        self.vertex_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.vertex_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.add_vertex_button.grid(row=0, column=2, padx=5, pady=5)
        self.remove_vertex_button.grid(row=0, column=3, padx=5, pady=5)

        self.canvas.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')

        self.import_button.grid(row=5, column=1, columnspan=1, padx=5, pady=5)
        self.save_button.grid(row=5, column=2, columnspan=1, padx=5, pady=5)
        self.clear_button.grid(row=5, column=3, columnspan=1, padx=5, pady=5)

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
    
    def bind_canvas_events(self):
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

    def set_state(self, state):
        self.current_state = state
        self.add_vertex_button.config(bg='grey' if self.current_state == 'add_vertex' else 'white')
        self.add_edge_button.config(bg='grey' if self.current_state == 'add_edge' else 'white')
        self.move_vertex_button.config(bg='grey' if self.current_state == 'move_vertex' else 'white')
    
    def on_canvas_click(self, event):
        if self.current_state == 'add_vertex':
            self.add_vertex(event.x, event.y)
        elif self.current_state == 'add_edge':
            self.start_edge(event.x, event.y)
        elif self.current_state == 'move_vertex':
            self.select_vertex(event.x, event.y)

    def on_canvas_drag(self, event):
        if self.current_state == 'move_vertex' and self.selected_vertex:
            self.move_vertex(event.x, event.y)
    

    def config_vertex(self, remove=False):
        label = self.vertex_entry.get()
        if label:
            try:
                vertex = self.graph.get_vertex_by_label(label) if remove else Vertex(label)
                self.graph.remove_vertex(vertex) if remove else self.graph.create_vertex(vertex)
                self.vertex_entry.delete(0, tk.END)
                self.update_output()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def config_edge(self, remove=False):
        v1_label = self.edge_v1_entry.get()
        v2_label = self.edge_v2_entry.get()
        v1 = self.graph.get_vertex_by_label(v1_label)
        v2 = self.graph.get_vertex_by_label(v2_label)
        try:
            self.graph.remove_edge(v1, v2) if remove else self.graph.create_edge(v1, v2)
            self.edge_v1_entry.delete(0, tk.END)
            self.edge_v2_entry.delete(0, tk.END)
            self.update_output()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def clear(self):
        clear_message = messagebox.askyesno("Clearing Graph", "Are you sure you want to clear graph?")
        if clear_message:
            self.graph.clear()
            self.update_output()
    
    def save(self):
        graph_name = simpledialog.askstring("Saving Graph", "What will you name this graph?")
        if graph_name:
            self.graph.name = graph_name
            self.graph.save()
            self.update_output()

    def update_output(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, str(self.graph))

if __name__ == "__main__":
    root = tk.Tk()
    app = Graphematics(root)
    root.mainloop()