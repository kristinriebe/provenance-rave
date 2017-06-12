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
router.register(r'collection', views.CollectionViewSet)

urlpatterns = [
    # index view:
    url(r'^$', views.IndexView.as_view(), name='index'),

    # include automatic rest api urls for models
    url(r'^api/', include(router.urls, namespace='api')),

    # provn of everything:
    url(r'^allprov/(?P<format>[a-zA-Z-]+)$', views.allprov, name='allprov'),
    url(r'^prettyprovn/$', views.prettyprovn, name='prettyprovn'),

    # form for observation id, basic or details:
    url(r'^form/$', views.get_observationId, name='get_observationId'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/(?P<detail_flag>[a-z]+)/$', views.observationid_detail, name='observationid_detail'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/(?P<detail_flag>[a-z]+)/graphjson$', views.observationid_detailjson, name='observationid_detailjson'),

    # provdal form
    url(r'^provdal/$', views.provdal, name='provdal'),
    url(r'^provdalform/$', views.provdal_form, name='provdal_form'),
    url(r'^provdal/graphjson$', views.provdal, name='provdal'),

    # graph overviews
    url(r'^graph/$', views.graph, name='graph'),
    url(r'^graph/graphjson$', views.fullgraphjson, name='graphjson'),
]

urlpatterns += router.urls
