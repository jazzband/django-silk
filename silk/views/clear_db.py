from django.db import connection
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Request, Response, SQLQuery, Profile


class ClearDBView(View):

    def _truncate_tables(self, models):
        raw_query = 'TRUNCATE TABLE {0};'
        truncate_query = [raw_query.format(m._meta.db_table) for m in models]
        truncate_query = ' '.join(truncate_query)
        query = 'SET FOREIGN_KEY_CHECKS = 0; {0} SET FOREIGN_KEY_CHECKS = 1;'.format(truncate_query)
        cursor = connection.cursor()
        cursor.execute(query)

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, *_, **kwargs):
        return render(request, 'silk/clear_db.html')

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def post(self, request, *_, **kwargs):
        context = {}
        if 'clear_all' in request.POST:
            self._truncate_tables([Response, SQLQuery, Profile, Request])
            tables = ['Response', 'SQLQuery', 'Profile', 'Request']
            context['msg'] = 'Cleared data for following silk tables: {0}'.format(', '.join(tables))
        return render(request, 'silk/clear_db.html', context=context)
