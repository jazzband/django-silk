from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^silky', include('silky.urls')),
                       url(r'^blog', include('blog.urls')),
                       )

