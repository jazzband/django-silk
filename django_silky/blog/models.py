from django.utils import timezone
import markdown2

from django.db import models
from django.db.models import DateTimeField, TextField, CharField, IntegerField, BooleanField


class Post(models.Model):
    published_date = DateTimeField(auto_now=False, default=timezone.now, db_index=True)
    modified_date = DateTimeField(auto_now=True, db_index=True)
    revision = IntegerField(null=True, blank=True)  # From dropbox
    markdown = TextField(default='', blank=True)
    published = BooleanField(default=False)

    @property
    def title(self):
        """derive the post title from the markdown if possible"""
        for line in self.markdown.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                try:
                    if line[1] != '#':
                        return line.split('#')[1].strip()
                except IndexError:
                    pass
        return 'Untitled'


    @property
    def dropbox_file_pattern(self):
        return '.%d.md' % self.pk

    @property
    def html(self):
        return markdown2.markdown(self.markdown, extras=['fenced-code-blocks'])