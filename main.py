from flask import Flask, request, render_template, jsonify, json
import modules.get_wiki_graph as wikig
from os import path, walk
import networkx as nx

app = Flask(__name__)


# Funcion que devuelve la pagina principal con las wikis disponibles en el servidor
@app.route('/')
def index():
    files = []
    for (dirpath, dirnames, filenames) in walk("data/"):
        files.extend(filenames)
        break
    dic_files = {}
    for file in files:
        dic_files[file] = path.splitext(file)[0]

    return render_template('index.html', dumps=dic_files)


# Funcion que calcula el grafo asociado a los datos recibidos y lo devuelve en el formato JSON requerido
@app.route('/_get_graph')
def get_graph():
    edge_weight = request.args.get('edgeweight', 1, type=int)
    clean_anonymous = request.args.get('anonimos', "off", type=str)
    if clean_anonymous == "on":
        clean_anonymous = True
    else:
        clean_anonymous = False

    clean_labels = request.args.get('labels', "off", type=str)
    if clean_labels == "on":
        clean_labels = True
    else:
        clean_labels = False

    graph_type = request.args.get('tipo', "users", type=str)
    layout = request.args.get('layout', "users", type=str)

    filename = "data/" + request.args.get('dump', "", type=str)
    if path.isfile(filename):
        if graph_type == "users":
            graph = wikig.get_graph_users(filename, clean_anonymous, clean_labels)
        else:
            graph = wikig.get_graph_pages(filename)

        wikig.remove_edge(graph, edge_weight)
        wikig.remove_isolates(graph)

        metrica = request.args.get('metrica', "degree", type=str)
        print(metrica)
        if metrica == "betweennes":
            result = wikig.add_betweennes_degree(graph)
        elif metrica == "eigenvector":
            result = wikig.add_eigenvector_degree(graph)
        elif metrica == "pagerank":
            result = wikig.add_page_rank_degree(graph)
        elif metrica == "clustering":
            result = wikig.add_clusterin_coefficient(graph)
        else:
            result = wikig.add_centrality_degree(graph)

        graph = result["graph"]
        min_value = result["min"]
        max_value = result["max"]
        map_peso = "mapData(weight, " + str(min_value) + ", " + str(max_value) + ", 2, 10)"
        print(map_peso)
        graph_json = wikig.convert2cytoscape_json(graph)
        return jsonify(result=graph_json, layout=layout,
                       num_nodos=graph.number_of_nodes(),
                       num_aristas=graph.number_of_edges(),
                       max=max_value, min=min_value, map=map_peso)
    # else:
    #     return jsonify(result=json.loads(render_template('data.json')),
    #                    layout="cose")
