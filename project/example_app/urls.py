from django.conf.urls import re_path
from . import views

app_name = 'example_app'
urlpatterns = [
                re_path(r'^$', views.index, name='index')
            ]
