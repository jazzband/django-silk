from django.conf.urls import re_path

from silk.views.clear_db import ClearDBView
from silk.views.profile_detail import ProfilingDetailView
from silk.views.profile_download import ProfileDownloadView
from silk.views.profile_dot import ProfileDotView
from silk.views.profiling import ProfilingView
from silk.views.raw import Raw
from silk.views.request_detail import RequestView
from silk.views.requests import RequestsView
from silk.views.sql import SQLView
from silk.views.sql_detail import SQLDetailView
from silk.views.summary import SummaryView
from silk.views.cprofile import CProfileView

app_name = 'silk'
urlpatterns = [
    re_path(r'^$', SummaryView.as_view(), name='summary'),
    re_path(r'^requests/$', RequestsView.as_view(), name='requests'),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/$',
        RequestView.as_view(),
        name='request_detail'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/sql/$',
        SQLView.as_view(),
        name='request_sql'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/sql/(?P<sql_id>[0-9]+)/$',
        SQLDetailView.as_view(),
        name='request_sql_detail'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/raw/$',
        Raw.as_view(),
        name='raw'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/pyprofile/$',
        ProfileDownloadView.as_view(),
        name='request_profile_download'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/json/$',
        ProfileDotView.as_view(),
        name='request_profile_dot'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/profiling/$',
        ProfilingView.as_view(),
        name='request_profiling'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/profile/(?P<profile_id>[0-9]+)/$',
        ProfilingDetailView.as_view(),
        name='request_profile_detail'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/profile/(?P<profile_id>[0-9]+)/sql/$',
        SQLView.as_view(),
        name='request_and_profile_sql'
    ),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/profile/(?P<profile_id>[0-9]+)/sql/(?P<sql_id>[0-9]+)/$',
        SQLDetailView.as_view(),
        name='request_and_profile_sql_detail'
    ),
    re_path(
        r'^profile/(?P<profile_id>[0-9]+)/$',
        ProfilingDetailView.as_view(),
        name='profile_detail'
    ),
    re_path(
        r'^profile/(?P<profile_id>[0-9]+)/sql/$',
        SQLView.as_view(),
        name='profile_sql'
    ),
    re_path(
        r'^profile/(?P<profile_id>[0-9]+)/sql/(?P<sql_id>[0-9]+)/$',
        SQLDetailView.as_view(),
        name='profile_sql_detail'
    ),
    re_path(r'^profiling/$', ProfilingView.as_view(), name='profiling'),
    re_path(r'^cleardb/$', ClearDBView.as_view(), name='cleardb'),
    re_path(
        r'^request/(?P<request_id>[a-zA-Z0-9\-]+)/cprofile/$',
        CProfileView.as_view(),
        name='cprofile'
    ),
]
