from six import BytesIO
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import View
from gprof2dot import DotWriter, PstatsParser, Profile
from silk.auth import login_possibly_required, permissions_possibly_required
from silk.models import Request


class PstatsMemoryParser(PstatsParser):

    def __init__(self, data):
        import pstats
        with BytesIO(data) as stream:
            self.stats = pstats.Stats(stream=stream)
        self.profile = Profile()
        self.function_ids = {}


class ProfileDotView(View):

    @method_decorator(login_possibly_required)
    @method_decorator(permissions_possibly_required)
    def get(self, request, request_id):
        silk_request = get_object_or_404(Request, pk=request_id, prof_file__isnull=False)
        parser = PstatsMemoryParser(silk_request.prof_file)
        parser.parse()
        cutoff = request.query_params.get('cutoff', 5)
        parser.profile.prune(cutoff / 100.0, 0.1 / 100.0, False)

        #response = FileResponse(silk_request.prof_file)
        #response['Content-Disposition'] = 'attachment; filename="{}"'.format(silk_request.prof_file.name)
        #return response
