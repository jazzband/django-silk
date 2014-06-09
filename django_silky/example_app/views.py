from django.shortcuts import render

# Create your views here.
from django.shortcuts import render_to_response
from example_app import models


def index(request):
    return render_to_response('example_app/index.html', {'blinds': models.Blind.objects.all()})
