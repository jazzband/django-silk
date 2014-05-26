from django.conf.urls import patterns, url

from silky.views.profile_detail import ProfilingDetailView
from silky.views.profiling import ProfilingView
from silky.views.request_detail import RequestView
from silky.views.root import RootView
from silky.views.sql import SQLView
from silky.views.sql_detail import SQLDetailView


urlpatterns = patterns('silky.views',
                       url(r'^/sql/(?P<sql_id>[0-9]*)/', SQLDetailView.as_view(),
                           name='sql_detail'),
                       url(r'^/request/(?P<request_id>[0-9]*)/sql/', SQLView.as_view({'get': 'get_request'}),
                           name='request_sql'),
                       url(r'^/profile/(?P<profile_id>[0-9]*)/sql/', SQLView.as_view({'get': 'get_profile'}),
                           name='profile_sql'),
                       url(r'^/profiling/', ProfilingView.as_view(), name='profiling'),
                       url(r'^/profile/(?P<profile_id>[0-9]*)/', ProfilingDetailView.as_view(), name='profile_detail'),
                       url(r'^/request/(?P<request_id>[0-9]*)/', RequestView.as_view(), name='request_detail'),
                       url(r'^/', RootView.as_view(), name='requests'))
