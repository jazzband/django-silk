__author__ = 'mtford'
from django.conf.urls import patterns, url

urlpatterns = patterns('pet_store.views',
                       url(r'^/pets/', 'pets', name='pets'))