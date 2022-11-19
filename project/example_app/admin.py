from django.contrib import admin
from django.urls import reverse

from .models import Blind, Category


class BlindAdmin(admin.ModelAdmin):
    list_display = ('desc', 'thumbnail', 'name', 'child_safe')
    list_editable = ('name', 'child_safe')

    def thumbnail(self, obj):
        try:
            img_tag = '<img src="%s" width="200px"/>' % obj.photo.url
        except ValueError:
            return ''
        url = self._blind_url(obj)
        return f'<a href="{url}">{img_tag}</a>'

    thumbnail.short_description = 'Photo'
    thumbnail.allow_tags = True

    def _blind_url(self, obj):
        url = reverse('admin:example_app_blind_change', args=(obj.id, ))
        return url

    def desc(self, obj):
        desc = str(obj)
        url = self._blind_url(obj)
        return f'<a href="{url}">{desc}</a>'

    desc.short_description = 'Blind'
    desc.allow_tags = True


admin.site.register(Blind, BlindAdmin)
admin.site.register(Category, admin.ModelAdmin)
