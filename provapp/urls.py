from django.conf.urls import url, include

from rest_framework import routers

from . import views

app_name = 'provapp'

# add automatically created urls:
router = routers.DefaultRouter()
router.register(r'activities', views.ActivityViewSet)
router.register(r'entities', views.EntityViewSet)
router.register(r'agents', views.AgentViewSet)
router.register(r'used', views.UsedViewSet)
router.register(r'wasgeneratedby', views.WasGeneratedByViewSet)
router.register(r'wasassociatedwith', views.WasAssociatedWithViewSet)
router.register(r'wasattributedto', views.WasAttributedToViewSet)
router.register(r'hadmember', views.HadMemberViewSet)
router.register(r'wasderivedfrom', views.WasDerivedFromViewSet)

urlpatterns = [
    # index view:
    url(r'^$', views.IndexView.as_view(), name='index'),

    # inlcude automatica rest api urls for models
    url(r'^api/', include(router.urls, namespace='api')),

    # provn of everything:
    url(r'^provn/$', views.provn, name='provn'),
    url(r'^prettyprovn/$', views.prettyprovn, name='prettyprovn'),

    # form for observation id, basic or details:
    url(r'^form/$', views.get_observationId, name='get_observationId'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/basic/$', views.provbasic, name='provbasic'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/basic/graphjson$', views.provbasicjson, name='provbasic'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/detail/$', views.provdetail, name='provdetail'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/detail/graphjson$', views.provdetailjson, name='provdetail'),
    url(r'^provdal/$', views.provdal, name='provdal'),
    url(r'^provdalform/$', views.provdal_form, name='provdal_form'),

    # graph overviews
    url(r'^graph/$', views.graph, name='graph'),
    url(r'^graph/graphjson$', views.fullgraphjson, name='graphjson'),
]

urlpatterns += router.urls
