from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hosts_table.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'core.views.index', name='index'),
    url(r'^version/$', 'core.views.version', name='version'),
    url(r'^collect/$', 'core.views.collect', name='collect'),
    url(r'^upload/$', 'core.views.upload', name='upload'),
    url(r'^raw/(.*?)/$', 'core.views.raw', name='raw'),
)
