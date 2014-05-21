from django.conf.urls import patterns, url

urlpatterns = patterns('silky.views',
                       url(r'^/sql/(?P<request_id>[0-9]*)/(?P<sql_id>[0-9]*)/', 'sql_detail', name='sql_detail'),
                       url(r'^/sql/(?P<request_id>[0-9]*)/', 'sql', name='sql'),
                       url(r'^/src/', 'source', name='source'),
                       url(r'^/profiling/(?P<request_id>[0-9]*)/', 'profiling', name='profiling'),
                       url(r'^/profile/(?P<profile_id>[0-9]*)/', 'profile', name='profile'),
                       url(r'^/request/(?P<request_id>[0-9]*)/', 'request', name='request'),
                       url(r'^/', 'requests', name='requests'))
