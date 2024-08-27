from .definitions import Vertex, Graph

def cartesian_product(canvas, graph1: Graph, graph2: Graph):
    new_graph = Graph(f"Cartesian: {graph1.name} x {graph2.name}")
    vertices1 = graph1.vertices
    vertices2 = graph2.vertices
    cartesian_vertices = [
        Vertex(canvas, (u.x + v.x)/2, (u.y + v.y)/2, labels=[u.id, v.id]) 
        for u in vertices1 for v in vertices2
    ]
    for vertex in cartesian_vertices:
        new_graph.create_vertex(vertex)

    for u in vertices1:
        vertices = new_graph.get_vertices_by_label(u.id)
        edges = graph1.edges
        for vertex in vertices:
            for neighbor in edges[vertex.id]:
                new_graph.create_edge(neighbor, vertex)
    for u in vertices2:
        vertices = new_graph.get_vertices_by_label(u.id)
        edges = graph2.edges
        for vertex in vertices:
            for neighbor in edges[vertex.id]:
                new_graph.create_edge(neighbor, vertex)

    new_graph.remove_all_labels()
    return new_graph

def tensor_product(graph1: Graph, graph2: Graph):
    pass
