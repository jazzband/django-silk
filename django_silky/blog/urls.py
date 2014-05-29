from django.conf.urls import patterns, url
from blog.feed import BlogPostFeed
from blog.views import AdminView

urlpatterns = patterns('blog.views',
                       url(r'^/$', 'index', name='index'),
                       url(r'^/admin/$', AdminView.as_view(), name='admin'),
                       url(r'^/blog/_feed/$', BlogPostFeed(), name='rss_feed'),
                       url(r'^/blog/(?P<post_id>[0-9]*)/$', 'post', name='post'),
                       url(r'^/smooth/$', 'smooth', name='smooth'))
