from django.urls import include, re_path

urlpatterns = [
    re_path(
        r'^example_app/',
        include('example_app.urls', namespace='example_app')
    ),
]
