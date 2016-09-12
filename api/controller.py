import json
import networkx as nx

from data import g


def test():
    return nx.readwrite.json_graph.node_link_data(g())


def miserables():
    with open('miserables.json', 'r') as infile:
        mis = json.load(infile)
    return mis
