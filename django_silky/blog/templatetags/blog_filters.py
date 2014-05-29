from django.template import Library
from django.utils.safestring import mark_safe

from blog.views import short_date


register = Library()


@register.filter(name='short_date')
def shrt(dt):
    return short_date(dt)


