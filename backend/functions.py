from .definitions import Vertex, Graph
from .utils import generate_random_id
from itertools import permutations


def check_isomorphism(graph1: Graph, graph2: Graph):
    if sorted(graph1.degrees()) != sorted(graph2.degrees()):
        return False

    vertices1 = list(graph1.edges.keys())
    vertices2 = list(graph2.edges.keys())

    for perm in permutations(vertices2):
        mapping = dict(zip(vertices1, perm))
        if all(
            set(graph1.edges[v1]) == set(mapping[v2] for v2 in graph2.edges[mapping[v1]])
            for v1 in vertices1
        ):
            return True
    return False

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
