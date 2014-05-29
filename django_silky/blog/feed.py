from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from blog.models import Post

__author__ = 'mtford'

class BlogPostFeed(Feed):

    title = "Michael Ford's blog"
    link = "/blog/"
    description = "Michael Ford's blog, software developer, UK"

    def items(self):
        return Post.objects.order_by('-published_date')[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.title

    def item_link(self, item):
        return reverse('post', args=[item.pk])
