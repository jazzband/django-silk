from time import sleep

# Create your views here.
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from example_app import models

from silk.profiling.profiler import silk_profile


def index(request):
    @silk_profile()
    def do_something_long():
        sleep(1.345)

    with silk_profile(name='Why do this take so long?'):
        do_something_long()
    return render(request, 'example_app/index.html', {'blinds': models.Blind.objects.all()})


class ExampleCreateView(CreateView):
    model = models.Blind
    fields = ['name']
    success_url = reverse_lazy('example_app:index')


def upload_test(request):
    """Test view for multipart/form-data with files and form fields."""
    if request.method == 'POST':
        data = {k: v for k, v in request.POST.items()}
        files = {k: v.name for k, v in request.FILES.items()}
        return JsonResponse({'fields': data, 'files': files})
    return render(request, 'example_app/upload_test.html')


@csrf_exempt
def upload_raw_body_test(request):
    """Test view that reads the raw multipart body, e.g. to verify a signature."""
    return JsonResponse({'length': len(request.body)})
