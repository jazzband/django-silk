from django.conf.urls import url
from . import views

app_name = 'example_app'
urlpatterns = [
                url(r'^$', views.index, name='index')
            ]
