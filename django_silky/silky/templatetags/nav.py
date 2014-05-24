from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def navactive(request, urls, *args):
    path = request.path
    urls = [reverse(url, args=args) for url in urls.split()]
    if path in urls:
        return "menu-item-selected"
    return ""