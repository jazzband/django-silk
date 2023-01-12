from django.urls import include, path

urlpatterns = [
    path(
        'example_app/',
        include('example_app.urls', namespace='example_app')
    ),
]
