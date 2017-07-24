from django.conf.urls import url, include
from . import views

app_name = 'raveprov'
urlpatterns = [
    # form for observation id, basic or details:
    url(r'^form/$', views.get_observationId, name='get_observationId'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/(?P<detail_flag>[a-z]+)/$', views.observationid_detail, name='observationid_detail'),
    url(r'^(?P<observation_id>[0-9a-zA-Z.:_-]+)/(?P<detail_flag>[a-z]+)/graphjson$', views.observationid_detailjson, name='observationid_detailjson'),
]