from django.template import Library
from django.urls import reverse

register = Library()


@register.simple_tag
def sql_detail_url(silk_request, profile, sql_query):
    if profile and silk_request:
        return reverse(
            "silk:request_and_profile_sql_detail",
            args=[silk_request.id, profile.id, sql_query.id],
        )
    elif profile:
        return reverse("silk:profile_sql_detail", args=[profile.id, sql_query.id])
    elif silk_request:
        return reverse("silk:request_sql_detail", args=[silk_request.id, sql_query.id])
