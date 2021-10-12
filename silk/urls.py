from django.urls import path

from silk.views.clear_db import ClearDBView
from silk.views.cprofile import CProfileView
from silk.views.profile_detail import ProfilingDetailView
from silk.views.profile_dot import ProfileDotView
from silk.views.profile_download import ProfileDownloadView
from silk.views.profiling import ProfilingView
from silk.views.raw import Raw
from silk.views.request_detail import RequestView
from silk.views.requests import RequestsView
from silk.views.sql import SQLView
from silk.views.sql_detail import SQLDetailView
from silk.views.summary import SummaryView

app_name = 'silk'
urlpatterns = [
    path(route='', view=SummaryView.as_view(), name='summary'),
    path(route='requests/', view=RequestsView.as_view(), name='requests'),
    path(
        route='request/<uuid:request_id>/',
        view=RequestView.as_view(),
        name='request_detail',
    ),
    path(
        route='request/<uuid:request_id>/sql/',
        view=SQLView.as_view(),
        name='request_sql',
    ),
    path(
        route='request/<uuid:request_id>/sql/<int:sql_id>/',
        view=SQLDetailView.as_view(),
        name='request_sql_detail',
    ),
    path(
        route='request/<uuid:request_id>/raw/',
        view=Raw.as_view(),
        name='raw',
    ),
    path(
        route='request/<uuid:request_id>/pyprofile/',
        view=ProfileDownloadView.as_view(),
        name='request_profile_download',
    ),
    path(
        route='request/<uuid:request_id>/json/',
        view=ProfileDotView.as_view(),
        name='request_profile_dot',
    ),
    path(
        route='request/<uuid:request_id>/profiling/',
        view=ProfilingView.as_view(),
        name='request_profiling',
    ),
    path(
        route='request/<uuid:request_id>/profile/<int:profile_id>/',
        view=ProfilingDetailView.as_view(),
        name='request_profile_detail',
    ),
    path(
        route='request/<uuid:request_id>/profile/<int:profile_id>/sql/',
        view=SQLView.as_view(),
        name='request_and_profile_sql',
    ),
    path(
        route='request/<uuid:request_id>/profile/<int:profile_id>/sql/<int:sql_id>/',
        view=SQLDetailView.as_view(),
        name='request_and_profile_sql_detail',
    ),
    path(
        route='profile/<int:profile_id>/',
        view=ProfilingDetailView.as_view(),
        name='profile_detail',
    ),
    path(
        route='profile/<int:profile_id>/sql/',
        view=SQLView.as_view(),
        name='profile_sql',
    ),
    path(
        route='profile/<int:profile_id>/sql/<int:sql_id>/',
        view=SQLDetailView.as_view(),
        name='profile_sql_detail',
    ),
    path(route='profiling/', view=ProfilingView.as_view(), name='profiling'),
    path(route='cleardb/', view=ClearDBView.as_view(), name='cleardb'),
    path(
        route='request/<uuid:request_id>/cprofile/',
        view=CProfileView.as_view(),
        name='cprofile',
    ),
]
