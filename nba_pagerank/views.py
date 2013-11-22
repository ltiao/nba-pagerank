from django.http import HttpResponse
from django.shortcuts import render
from datasets.data import graph
import networkx as nx
from networkx.readwrite import json_graph
import numpy as np
from django.core.serializers.json import DjangoJSONEncoder
import json

def home(request):
    print request.GET.getlist('team')
    return render(request, 'base.html')
    
def visualize(request):
    G = graph('2013-14', include=['MIA', 'ATL', 'CHA', 'ORL', 'WAS', 'IND', 'CHI', 'DET', 'CLE', 'MIL'])
    data = json_graph.node_link_data(G)
    if request.is_ajax():
        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
    else:
        M = nx.pagerank_numpy(G)
        for team in data['nodes']:
            team_id = team['id']
            team['pagerank'] = M[team_id]
            team['in_deg'] = G.in_degree(team_id)
            team['out_deg'] = G.out_degree(team_id)
            team['deg'] = G.degree(team_id)
            team['pct'] = team['in_deg']/float(team['deg'])
            
        return render(request, 'vis2.html', {'data': data})

# TODO: Filter by team
# TODO: Filter by time interval
# TODO: Filter by season
def adj(request):
    G = graph('2013-14')
    teams = ['MIA', 'ATL', 'CHA', 'ORL', 'WAS']
    H = G.subgraph([team_id for team_id in G.nodes() if G.node[team_id]['abbr'] in teams])
    nodelist = sorted(H.nodes(), key = lambda a: H.node[a]['abbr'])
    return render(request, 'adjacency_matrix.html', {'data': np.array(nx.to_numpy_matrix(H, nodelist), dtype='int'), 'teams': [H.node[a]['abbr'] for a in nodelist]})