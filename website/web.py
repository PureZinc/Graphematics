from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)

graphs = {}

def get_storage(path, database):
    folder_path = os.path.join(os.path.dirname(__file__), path)
    folder_path = os.path.normpath(folder_path)
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                database[filename.replace('.json', '')] = data
get_storage('../storage/graphs', graphs)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/graphs')
def graph_page():
    return render_template("graphs.html", graphs=graphs)

@app.route('/graphs/<graph_name>')
def graph_detail(graph_name):
    vertex = graphs[graph_name]
    if vertex is None:
        return "Graph not found", 404
    details = {
        "graph_name": graph_name,
        "graph_details": vertex,
        "num_vertices": len(list(vertex)),
        "num_edges": sum([len(v["neighbors"]) for v in vertex.values()])//2,
        "description": "No description yet"
    }
    return render_template("graph_details.html", **details)

@app.route('/api/graphs', methods=['GET'])
def get_vertices():
    return jsonify(graphs)

@app.route('/api/<graph_name>', methods=['GET'])
def get_vertex(graph_name):
    vertex = graphs[graph_name]
    if vertex is None:
        return jsonify({"error": "Vertex not found"}), 404
    return jsonify(vertex)

if __name__ == '__main__':
    app.run(debug=True)