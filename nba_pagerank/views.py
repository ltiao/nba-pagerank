from django.http import HttpResponse
from django.shortcuts import render_to_response
from datasets.data import graph
import networkx as nx
import numpy as np

def home(request):
    return HttpResponse("Hello from django, try out <a href='/admin/'>/admin/</a>\n")
    
def test(request):
    G = graph('2013-14')
    nodelist = sorted(G.nodes(), key = lambda a: G.node[a]['abbr'])
    return render_to_response('base.html', {'data': np.array(nx.to_numpy_matrix(G, nodelist), dtype='int'), 'teams': [G.node[a]['abbr'] for a in nodelist]})