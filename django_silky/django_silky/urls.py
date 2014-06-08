from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^silk', include('silk.urls', namespace='silk', app_name='silk')),
                       url(r'^example_app', include('example_app.urls')),
                       url(r'^admin/', include(admin.site.urls)),

)

