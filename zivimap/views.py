from django.shortcuts import render
from django.core import serializers
from zivimap.api import *
from zivimap.models import WorkSpec, Address
import json

def all_resources(request, resource, queryset):
    objects = []
    for m in queryset:
        bundle = resource.build_bundle(obj=m, request=request)
        bundle = resource.full_dehydrate(bundle)
        objects.append(bundle)
    return resource.serialize(None, objects, 'application/json')

def index(request):
    addresses = all_resources(request, AddressResource(), Address.objects.all())
    ws = all_resources(request, MapSearchResource(), WorkSpec.objects.all())
    context = {'addresses': addresses,
               'workspecs' : ws}
    return render(request, 'index.html', context)
