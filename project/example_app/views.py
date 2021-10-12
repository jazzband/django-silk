from time import sleep

# Create your views here.
from django.shortcuts import render
from example_app import models
from silk.profiling.profiler import silk_profile


def index(request):
    @silk_profile()
    def do_something_long():
        sleep(1.345)

    with silk_profile(name="Why do this take so long?"):
        do_something_long()
    return render(
        request, "example_app/index.html", {"blinds": models.Blind.objects.all()}
    )
