from django.urls import path

from . import views

app_name = 'example_app'
urlpatterns = [
    path(route='', view=views.index, name='index'),
    path(route='create', view=views.ExampleCreateView.as_view(), name='create'),
    path(route='upload', view=views.upload_test, name='upload_test'),
    path(route='upload-raw', view=views.upload_raw_body_test, name='upload_raw_body_test'),
]
