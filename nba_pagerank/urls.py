from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^blog/', include('blog.urls')),
    # url(r'^$', 'nba_pagerank.views.home', name='home'),
    url(r'^$', 'nba_pagerank.views.test', name='home'),
    url(r'^admin/', include(admin.site.urls)),
)
