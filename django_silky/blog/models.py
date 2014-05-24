import markdown2

from django.db import models
from django.db.models import DateTimeField, TextField



class Post(models.Model):
    date = DateTimeField(auto_now=True, db_index=True)
    markdown = TextField(default='', blank=True)

    @property
    def html(self):
        return markdown2.markdown(self.markdown, extras=['fenced-code-blocks'])


