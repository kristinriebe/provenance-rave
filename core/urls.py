from django.conf.urls import url
from . import views

app_name = 'core'

urlpatterns = [
    # index view
    url(r'^$', views.index, name='index') # for simple index-view
]