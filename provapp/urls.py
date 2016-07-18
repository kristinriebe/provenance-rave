from django.conf.urls import url

from . import views

app_name = 'provapp'
urlpatterns = [
    # ex: /provapp/5/
    url(r'^activities/(?P<activity_id>[0-9a-zA-Z.:_-]+)/myjson/$', views.myjson, name='myjson'),
    
    # actually used:
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^activities/(?P<pk>[0-9a-zA-Z.:_-]+)/$', views.ActivityDetailView.as_view(), name='activity_detail'),
    url(r'^activities/$', views.ActivitiesView.as_view(), name='activities'),
    url(r'^activities/(?P<pk>[0-9a-zA-Z.:_-]+)/provjson/$', views.ActivityDetailJsonView.as_view(), name='activity_detail_json'),
    url(r'^activities/(?P<activity_id>[0-9a-zA-Z.:_-]+)/json/$', views.graphjson, name='graphjson'),
    url(r'^activities/(?P<pk>[0-9a-zA-Z.:_-]+)/xml/$', views.ActivityDetailXmlView.as_view(), name='activity_detail_xml'),

    url(r'^entities/$', views.EntitiesView.as_view(), name='entities'),
    url(r'^entities/(?P<pk>[0-9a-zA-Z.:_-]+)/$', views.EntityDetailView.as_view(), name='entity_detail'),
    url(r'^agents/$', views.AgentsView.as_view(), name='agents'),
    url(r'^agents/(?P<pk>[0-9a-zA-Z.:_-]+)/$', views.AgentDetailView.as_view(), name='agent_detail'),
    url(r'^provn/$', views.provn, name='provn'),
    url(r'^prettyprovn/$', views.prettyprovn, name='prettyprovn'),

    url(r'^form/$', views.get_observationId, name='get_observationId'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/basic/$', views.provbasic, name='provbasic'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/basic/json$', views.provbasicjson, name='provbasic'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/detail/$', views.provdetail, name='provdetail'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/detail/json$', views.provdetailjson, name='provdetail'),
    

# not used?
    url(r'^activities/(?P<pk>[0-9a-zA-Z.:_-]+)/xml/$', views.ActivityDetailXmlView.as_view(), name='activity_detail_xml'),
    url(r'^graph/$', views.graph, name='graph'),
    url(r'^graph/fullgraphjson$', views.fullgraphjson, name='fullgraphjson'),
    #url(r'^provdetail?observation_id=(?P<observation_id>[0-9a-zA-Z.:_]+)$', views.provdetail, name='provdetail'), # not working
]