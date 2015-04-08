from django.contrib import admin
from django.core.urlresolvers import reverse
from .models import Blind


class BlindAdmin(admin.ModelAdmin):
    list_display = ('desc', 'thumbnail', 'name', 'child_safe')
    list_editable = ('name', 'child_safe')

    def thumbnail(self, obj):
        try:
            img_tag = u'<img src="%s" width="200px"/>' % obj.photo.url
        except ValueError:
            return u''
        url = self._blind_url(obj)
        return u'<a href="%s">%s</a>' % (url, img_tag)

    thumbnail.short_description = 'Photo'
    thumbnail.allow_tags = True

    def _blind_url(self, obj):
        url = reverse('admin:example_app_blind_change', args=(obj.id, ))
        return url

    def desc(self, obj):
        desc = str(obj)
        url = self._blind_url(obj)
        return u'<a href="%s">%s</a>' % (url, desc)

    desc.short_description = 'Blind'
    desc.allow_tags = True



admin.site.register(Blind, BlindAdmin)
