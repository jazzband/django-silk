import logging

from django.test import TestCase

from blog.models import Post


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
