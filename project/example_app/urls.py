from django.conf.urls import patterns, url

urlpatterns = patterns('example_app.views',
                       url(r'^$', 'index', name='index'))
