from django.conf.urls import include, url

urlpatterns = [
    url(r"^example_app/", include("example_app.urls", namespace="example_app")),
]
