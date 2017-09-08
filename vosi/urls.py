from django.conf.urls import url, include
from . import views

app_name = 'vosi'

urlpatterns = [
    # vosi endpoints required by dali: capabilities, availability
    url(r'^availability/$', views.vosi_availability, name='vosi_availability'),
    url(r'^capabilities/$', views.vosi_capabilities, name='vosi_capabilities'),
]