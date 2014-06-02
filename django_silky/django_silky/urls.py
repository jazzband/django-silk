from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^silk', include('silk.urls', namespace='silk'))
                       )

