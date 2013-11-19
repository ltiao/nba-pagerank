from django.http import HttpResponse
from django.shortcuts import render_to_response
import numpy as np

def home(request):
    return HttpResponse("Hello from django, try out <a href='/admin/'>/admin/</a>\n")
    
def test(request):
    return render_to_response('base.html', {'data': np.random.rand(10,5)})