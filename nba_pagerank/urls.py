from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'nba_pagerank.views.home', name='home'),
    url(r'^adj/$', 'nba_pagerank.views.adj', name='adjacency'),
    url(r'^graph/$', 'nba_pagerank.views.visualize', name='graph'),
    url(r'^xhr_graph_data/$', 'nba_pagerank.views.xhr_graph_data', name='xhr_graph_data'),
    url(r'^admin/', include(admin.site.urls)),
)
