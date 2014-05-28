from datetime import timedelta
import logging

from django.test import TestCase
from django.utils import timezone

from blog.models import Post
from blog.views import short_date


logger = logging.getLogger('blog')


class TestMarkdown(TestCase):
    def test_highlight(self):
        markdown = """```python
    if True:
        print "hi"
```"""
        post = Post(markdown=markdown)
        post.save()
        post_html = post.html
        print post_html
        self.assertIn('codehilite', post_html)


class TestShortDate(TestCase):

    def test(self):
        self.assertEqual('59s', short_date(timezone.now()-timedelta(seconds=59)))
        self.assertEqual('1m', short_date(timezone.now()-timedelta(seconds=60)))
        self.assertEqual('59m', short_date(timezone.now()-timedelta(seconds=60*59)))
        self.assertEqual('1h', short_date(timezone.now()-timedelta(seconds=60*60)))
        self.assertEqual('2h', short_date(timezone.now()-timedelta(seconds=60*60*2)))
        self.assertEqual('20d', short_date(timezone.now()-timedelta(days=20)))
        self.assertEqual('1y', short_date(timezone.now()-timedelta(days=365)))
        self.assertEqual('1y', short_date(timezone.now()-timedelta(days=400)))
        self.assertEqual('1y', short_date(timezone.now()-timedelta(days=450)))
        self.assertEqual('2y', short_date(timezone.now()-timedelta(days=800)))
        self.assertEqual('1m', short_date(timezone.now()-timedelta(days=40)))
        self.assertEqual('2m', short_date(timezone.now()-timedelta(days=70)))
        self.assertEqual('2m', short_date(timezone.now()-timedelta(days=70)))
        self.assertEqual('2m', short_date(timezone.now()-timedelta(days=70)))