#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
   get_graph.py

   Descp: Script para generar a partir del dump de una wiki el grafo asociado.
   Puede generar el grafo en el que los usuarios son los nodos y las paginas las aristas o
   al reves. Una vez generado lo exporta en diversos formatos para ser visualizado con
   otras herramientas y calcula distintas medidas sobre el grafo para facilitar su analisis.

   Created on: 09-feb-2018

   Copyright 2018 David Fdez Villa
"""

import sys
import csv
import json

import networkx as nx
import os.path


#Funcion para obtener de un dump el grafo en el que los usuarios son los nodos
def get_graph_users(filename, clean_anonymous, clean_anonymous_label):
    with open(filename, newline='') as csvfile:
        dict_reader = csv.DictReader(csvfile, delimiter=';')
        dict_user = {}
        for row in dict_reader:
            page_id = row['page_id']
            contributor_id = row['contributor_id']
            contributor_name = row['contributor_name']
            if contributor_name == "Anonymous" and clean_anonymous:
                continue
            if contributor_name == "Anonymous" and clean_anonymous_label:
                contributor_name = ""
            if page_id not in dict_user:
                dict_user[page_id] = [(contributor_id, contributor_name)]
            elif (contributor_id, contributor_name) not in dict_user[page_id]:
                dict_user[page_id].append((contributor_id, contributor_name))

        return get_graph_from_dict(dict_user)


# Funcion para obtener de un dump el grafo en el que las paginas son los nodos
def get_graph_pages(filename):
    with open(filename, newline='') as csvfile:
        dict_reader = csv.DictReader(csvfile, delimiter=';')
        dict_pages = {}
        for row in dict_reader:
            page_id = row['page_id']
            page_title = row['page_title']
            contributor_id = row['contributor_id']
            if contributor_id not in dict_pages:
                dict_pages[contributor_id] = [(page_id, page_title)]
            elif (page_id, page_title) not in dict_pages[contributor_id]:
                dict_pages[contributor_id].append((page_id, page_title))
        return get_graph_from_dict(dict_pages)


# Funcion para obtener un grafo a partir del diccionario
def get_graph_from_dict(dict_graph):
    graph = nx.Graph()
    for k, v in dict_graph.items():
        for node_id, node_label in v:
            graph.add_node(node_id, label=node_label, weight=1, max_weight=1, min_weight=1)
        for i in range(0, len(v) - 1):
            node1 = v[i][0]
            for j in range(i + 1, len(v)):
                node2 = v[j][0]
                if graph.has_edge(node1, node2):
                    graph[node1][node2]['weight'] += 1
                else:
                    graph.add_edge(node1, node2, weight=1)
    return graph


# Funcion para analizar el grafo
def analyse_graph(graph, save_name):
    with open(save_name + "_analysis.txt", 'w') as analysis_file:
        menu = {'1': "Degree centrality of nodes.",
                '2': "Betweennes centrality of nodes.",
                '3': "Eigenvector centrality of nodes.",
                '4': "PageRank of nodes",
                '5': "HITS of nodes",
                '6': "Clustering coefficient of nodes",
                '7': "Average clustering coefficient of the graph",
                '8': "Finalize analysis"}
        while True:
            print("\nAnalysis options: ")

            for number in sorted(menu.keys()):
                print(number, menu[number])

            selection = input("Select format [1-8]:").strip()
            if selection == '1':
                result = nx.degree_centrality(graph)
                analysis_file.write("Degree centrality of nodes\n")
                analysis_file.write("Node_id, Node_degree \n")
                min_value = float('inf')
                max_value = 0.0
                for node_id, node_degree in result.items():
                    analysis_file.write(node_id + "," + str(node_degree) + "\n")
                    max_value = max(max_value, node_degree)
                    min_value = min(min_value, node_degree)
                    graph.node[node_id]["weight"] = node_degree

                for node_id in graph.nodes():
                    graph.node[node_id]["max_weight"] = max_value
                    graph.node[node_id]["min_weight"] = min_value
                analysis_file.write("\n")
                print("\nDone!\n")
            elif selection == '2':
                result = nx.betweenness_centrality(graph)
                analysis_file.write("Betweennes centrality of nodes\n")
                analysis_file.write("Node_id, Node_betweennes \n")
                for node_id, node_betweennes in result.items():
                    analysis_file.write(node_id + "," + str(node_betweennes) + "\n")
                analysis_file.write("\n")
                print("\nDone!\n")
            elif selection == '3':
                result = nx.eigenvector_centrality(graph)
                analysis_file.write("Eigenvector centrality of nodes\n")
                analysis_file.write("Node_id, Node_eigenvector \n")
                for node_id, node_eigenvector in result.items():
                    analysis_file.write(node_id + "," + str(node_eigenvector) + "\n")
                analysis_file.write("\n")
                print("\nDone!\n")
            elif selection == '4':
                result = nx.pagerank(graph)
                analysis_file.write("PageRank of nodes\n")
                analysis_file.write("Node_id, Node_PageRank \n")
                for node_id, node_page_rank in result.items():
                    analysis_file.write(node_id + "," + str(node_page_rank) + "\n")
                analysis_file.write("\n")
                print("\nDone!\n")
            elif selection == '5':
                result = nx.hits(graph)
                analysis_file.write("HITS of nodes\n")
                hubs = result[0]
                analysis_file.write("Node_id, Node_Hubs \n")
                for node_id, node_hubs in hubs.items():
                    analysis_file.write(node_id + "," + str(node_hubs) + "\n")
                analysis_file.write("\n")

                authorities = result[1]
                analysis_file.write("Node_id, Node_Authorities \n")
                for node_id, node_authorities in authorities.items():
                    analysis_file.write(node_id + "," + str(node_authorities) + "\n")
                analysis_file.write("\n")
                print("\nDone!\n")
            elif selection == '6':
                result = nx.clustering(graph)
                analysis_file.write("Clustering coefficient of nodes\n")
                analysis_file.write("Node_id, Node_Clustering_Coefficient \n")
                for node_id, node_clc in result.items():
                    analysis_file.write(node_id + "," + str(node_clc) + "\n")
                analysis_file.write("\n")
                print("\nDone!\n")
            elif selection == '7':
                result = nx.average_clustering(graph)
                analysis_file.write("Average clustering coefficient of the graph: " + str(result) + "\n")
                analysis_file.write("\n")
                print("\nDone!\n")
            elif selection == '8':
                return
            else:
                print("Unknown option selected!")


# Funcion para calcular el grado de centralidad y anadirlo a los nodos como atributo
def add_centrality_degree(graph):
    result = nx.degree_centrality(graph)
    min_value = float('inf')
    max_value = 0.0
    for node_id, node_degree in result.items():
        max_value = max(max_value, node_degree)
        min_value = min(min_value, node_degree)
        graph.node[node_id]["weight"] = node_degree

    return {"graph": graph, "max": max_value, "min": min_value}


# Funcion para calcular cercania y anadirlo a los nodos como atributo
def add_betweennes_degree(graph):
    result = nx.betweenness_centrality(graph)
    min_value = float('inf')
    max_value = 0.0
    for node_id, node_degree in result.items():
        max_value = max(max_value, node_degree)
        min_value = min(min_value, node_degree)
        graph.node[node_id]["weight"] = node_degree


    return {"graph": graph, "max": max_value, "min": min_value}


# Funcion para calcular el eigenvector y anadirlo a los nodos como atributo
def add_eigenvector_degree(graph):
    result = nx.eigenvector_centrality(graph)
    min_value = float('inf')
    max_value = 0.0
    for node_id, node_degree in result.items():
        max_value = max(max_value, node_degree)
        min_value = min(min_value, node_degree)
        graph.node[node_id]["weight"] = node_degree

    return {"graph": graph, "max": max_value, "min": min_value}


# Funcion para calcular el PageRank y anadirlo a los nodos como atributo
def add_page_rank_degree(graph):
    result = nx.pagerank(graph)
    min_value = float('inf')
    max_value = 0.0
    for node_id, node_degree in result.items():
        max_value = max(max_value, node_degree)
        min_value = min(min_value, node_degree)
        graph.node[node_id]["weight"] = node_degree

    return {"graph": graph, "max": max_value, "min": min_value}


# Funcion para calcular el coeficiente de clustering y anadirlo a los nodos como atributo
def add_clusterin_coefficient(graph):
    result = nx.clustering(graph)
    min_value = float('inf')
    max_value = 0.0
    for node_id, node_degree in result.items():
        max_value = max(max_value, node_degree)
        min_value = min(min_value, node_degree)
        graph.node[node_id]["weight"] = node_degree

    return {"graph": graph, "max": max_value, "min": min_value}


# Funcion para guardar el grafo en diferentes formatos
def save_graph(graph, save_name):
    menu = {'1': "GEXF", '2': "GML", '3': "GraphML", '4': "Pajek", '5': "Exit"}
    while True:
        print("\nSupported formats: ")

        for number in sorted(menu.keys()):
            print(number, menu[number])

        selection = input("Select format [1-6]:").strip()
        if selection == '1':
            nx.write_gexf(graph, save_name + ".gexf")
            print("Saved in GEXF format")
        elif selection == '2':
            nx.write_gml(graph, save_name + ".gml")
            print("Saved in GML format")
        elif selection == '3':
            nx.write_graphml(graph, save_name + ".graphml")
            print("Saved in GraphML format")
        elif selection == '4':
            nx.write_pajek(graph, save_name + ".net")
            print("Saved in Pajek format")
        elif selection == '5':
            return
        else:
            print("Unknown Format Selected!")


# funcion para convertir grafo de network x
# en formato JSON de Cytoscape.js
def convert2cytoscape_json(G):
    dict_final = {"nodes": [], "edges": []}
    for node in G.nodes(data=True):
        dict_tmp = {"data": {}}
        dict_tmp["data"]["id"] = node[0]
        dict_tmp["data"]["label"] = node[1]['label']
        dict_tmp["data"]["weight"] = node[1]['weight']
        dict_tmp["data"]["max_weight"] = node[1]['max_weight']
        dict_tmp["data"]["min_weight"] = node[1]['min_weight']
        dict_final["nodes"].append(dict_tmp.copy())
    for edge in G.edges(data=True):
        dict_tmp = {"data": {}}
        dict_tmp["data"]["id"] = edge[0] + edge[1]
        dict_tmp["data"]["source"] = edge[0]
        dict_tmp["data"]["target"] = edge[1]
        dict_tmp["data"]['weight'] = edge[2]['weight']
        dict_final["edges"].append(dict_tmp)

    return dict_final


# Se asegura que exista el directorio y, si no, lo crea
def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


# Elimina los nodos aislados
def remove_isolates(graph):
    graph.remove_nodes_from(list(nx.isolates(graph)))
    return


# Elimina las aristas por debajo del peso minimo
def remove_edge(graph, min_weight):
    edges_2_remove = []
    for k, v in graph.edges():
        if graph[k][v]['weight'] < min_weight:
            edges_2_remove.append((k, v))
    graph.remove_edges_from(edges_2_remove)
    return


# Funcion principal del script
def main():
    help_user = """This script generates the graph asociated to the wiki\n
            Syntax: python3 get_wiki_graph dump_of_wiki.csv"""

    if (len(sys.argv)) == 2:
        if sys.argv[0] == 'help':
            print(help_user)
            exit(0)

        filename = sys.argv[1]
        if os.path.isfile(filename):
            directory = "data/"
            print("Retrieving graph for: " + filename)
            menu = {'1': "Generate user graph", '2': "Generate page graph", '3': "Exit"}
            while True:
                print("\nMenu:")
                for number in sorted(menu.keys()):
                    print(number, menu[number])

                selection = input("\nPlease Select [1-3]:").strip()
                if selection == '1':
                    graph = get_graph_users(filename)
                    name_to_save = directory + os.path.splitext(filename)[0] + "_users"
                    print("Done!")
                    break
                elif selection == '2':
                    graph = get_graph_pages(filename)
                    name_to_save = directory + os.path.splitext(filename)[0] + "_pages"
                    print("Done!")
                    break
                elif selection == '3':
                    print("Ciao!")
                    exit(0)
                else:
                    print("Unknown Option Selected!")
            print("\nNodes:" + str(graph.number_of_nodes()))
            print("\nEdges:" + str(graph.number_of_edges()))
            while True:
                try:
                    min_weight = int(input("\nRemove edges with weight below: "))
                    remove_edge(graph, min_weight)
                    print("\nEdges:" + str(graph.number_of_edges()))
                    break
                except ValueError:
                    print("That was no valid number.  Try again...")

            while True:
                selection = input("\nAnalyse graph? [Y/N]:").strip().lower()
                if selection == 'y':
                    ensure_dir(directory)
                    analyse_graph(graph, name_to_save)
                    break
                elif selection == 'n':
                    break
                else:
                    print("Invalid answer!")

            while True:
                selection = input("\nSave graph? [Y/N]:").strip().lower()
                if selection == 'y':
                    ensure_dir(directory)
                    save_graph(graph, name_to_save)
                    break
                elif selection == 'n':
                    break
                else:
                    print("Invalid answer!")

            convert2cytoscape_json(graph)

            print("Ciao!")
            exit(0)
        else:
            print("Error: File doesn't exist")
            exit(1)

    else:
        print("Error: Invalid number of arguments. Please specify one dumpfile", file=sys.stderr)
        print(help_user)
        exit(1)


if __name__ == '__main__':
    main()
