from django.http import HttpResponse
from django.shortcuts import render
from datasets.data import graph
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np
from django.core.serializers.json import DjangoJSONEncoder
import json

def home(request):
    return render(request, 'base.html')
    
def visualize(request):
    return render(request, 'vis2.html')
        
def xhr_graph_data(request):
    G = graph('2013-14')
    teams = ['MIA', 'ATL', 'CHA', 'ORL', 'WAS', 'IND', 'CHI', 'DET', 'CLE', 'MIL']
    H = G.subgraph([team_id for team_id in G.nodes() if G.node[team_id]['abbr'] in teams])
    data = json.dumps(json_graph.node_link_data(H), cls=DjangoJSONEncoder)
    return HttpResponse(data, 'json')
        
# TODO: Filter by team
# TODO: Filter by time interval
# TODO: Filter by season
def adj(request):
    G = graph('2013-14')
    teams = ['MIA', 'ATL', 'CHA', 'ORL', 'WAS']
    H = G.subgraph([team_id for team_id in G.nodes() if G.node[team_id]['abbr'] in teams])
    nodelist = sorted(H.nodes(), key = lambda a: H.node[a]['abbr'])
    return render(request, 'adjacency_matrix.html', {'data': np.array(nx.to_numpy_matrix(H, nodelist), dtype='int'), 'teams': [H.node[a]['abbr'] for a in nodelist]})