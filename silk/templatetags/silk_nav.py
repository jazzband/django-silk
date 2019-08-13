from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def navactive(request, urls, *args, **kwargs):
    path = request.path
    urls = [reverse(url, args=args) for url in urls.split()]
    if path in urls:
        cls = kwargs.get('class', None)
        if not cls:
            cls = "menu-item-selected"
        return cls
    return ""
