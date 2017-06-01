from django.conf.urls import url

from . import views

app_name = 'provapp'
urlpatterns = [
    # index view:
    url(r'^$', views.IndexView.as_view(), name='index'),

    # activities:
    url(r'^activities/$', views.ActivitiesView.as_view(), name='activities'),
    url(r'^activities/(?P<pk>[0-9a-zA-Z.:_-]+)/$', views.ActivityDetailView.as_view(), name='activity_detail'),
    # - graph json:
    url(r'^activities/(?P<activity_id>[0-9a-zA-Z.:_-]+)/graphjson/$', views.graphjson, name='graphjson'),
    # - test different serialisation formats:
    url(r'^activities/(?P<pk>[0-9a-zA-Z.:_-]+)/json/$', views.ActivityDetailJsonView.as_view(), name='activity_detail_json'),
    url(r'^activities/(?P<pk>[0-9a-zA-Z.:_-]+)/xml/$', views.ActivityDetailXmlView.as_view(), name='activity_detail_xml'),
    url(r'^activities/(?P<activity_id>[0-9a-zA-Z.:_-]+)/myjson/$', views.myjson, name='myjson'),

    # entities:
    url(r'^entities/$', views.EntitiesView.as_view(), name='entities'),
    url(r'^entities/(?P<pk>[0-9a-zA-Z.:_-]+)/$', views.EntityDetailView.as_view(), name='entity_detail'),

    # agents:
    url(r'^agents/$', views.AgentsView.as_view(), name='agents'),
    url(r'^agents/(?P<pk>[0-9a-zA-Z.:_-]+)/$', views.AgentDetailView.as_view(), name='agent_detail'),

    # provn of everything:
    url(r'^provn/$', views.provn, name='provn'),
    url(r'^prettyprovn/$', views.prettyprovn, name='prettyprovn'),

    # form for observation id, basic or details:
    url(r'^form/$', views.get_observationId, name='get_observationId'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/basic/$', views.provbasic, name='provbasic'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/basic/graphjson$', views.provbasicjson, name='provbasic'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/detail/$', views.provdetail, name='provdetail'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/detail/graphjson$', views.provdetailjson, name='provdetail'),
    url(r'^obsid/$', views.provdal_obsid, name='provdal_obsid'),

    # graph overviews
    url(r'^graph/$', views.graph, name='graph'),
    url(r'^graph/graphjson$', views.fullgraphjson, name='graphjson'),
]
