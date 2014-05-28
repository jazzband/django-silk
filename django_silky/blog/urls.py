from django.conf.urls import patterns, url

urlpatterns = patterns('blog.views',
                       url(r'^/$', 'index', name='index'),
                       url(r'^/admin/$', 'admin', name='admin'),
                       url(r'^/smooth/', 'smooth', name='smooth'))
