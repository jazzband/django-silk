from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views
from django.urls import path

urlpatterns = [
    path(
        route='silk/',
        view=include('silk.urls', namespace='silk'),
    ),
    path(
        route='example_app/',
        view=include('example_app.urls', namespace='example_app'),
    ),
    path(route='admin/', view=admin.site.urls),
]



urlpatterns += [
    path(
        route='login/',
        view=views.LoginView.as_view(
            template_name='example_app/login.html'
        ),
        name='login',
    ),
]



urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
