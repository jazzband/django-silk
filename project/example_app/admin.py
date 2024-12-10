from django.contrib import admin
from django.urls import reverse

from .models import Blind


@admin.register(Blind)
class BlindAdmin(admin.ModelAdmin):
    list_display = ("desc", "thumbnail", "name", "child_safe")
    list_editable = ("name", "child_safe")

    @admin.display(description="Photo")
    def thumbnail(self, obj):
        try:
            img_tag = '<img src="%s" width="200px"/>' % obj.photo.url
        except ValueError:
            return ""
        url = self._blind_url(obj)
        return f'<a href="{url}">{img_tag}</a>'

    def _blind_url(self, obj):
        url = reverse("admin:example_app_blind_change", args=(obj.id,))
        return url

    @admin.display(description="Blind")
    def desc(self, obj):
        desc = str(obj)
        url = self._blind_url(obj)
        return f'<a href="{url}">{desc}</a>'
