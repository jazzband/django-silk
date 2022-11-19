from django.urls import path

from . import views

app_name = 'example_app'
urlpatterns = [
    path(route='', view=views.index, name='index'),
    path(route='create', view=views.ExampleCreateView.as_view(), name='create'),
]
