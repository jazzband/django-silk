from django.test import TestCase
from blog.models import Post


class TestMarkdown(TestCase):

    def test_highlight(self):
        markdown = """```python
    if True:
        print "hi"
```"""
        post = Post(markdown=markdown)
        post.save()
        self.assertIn('codehilite', post.html)