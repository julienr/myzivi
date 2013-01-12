from django.shortcuts import render
from django.core import serializers
from zivimap.api import WorkSpecResource
from zivimap.models import WorkSpec
import json

def index(request):
    # Return all workspecs
    # TODO: This is pretty massive... Better use server-side clustering
    ws = WorkSpecResource()
    allws = WorkSpec.objects.all()
    objects = []
    for m in allws:
        bundle = ws.build_bundle(obj=m, request=request)
        bundle = ws.full_dehydrate(bundle)
        objects.append(bundle)

    context = {'workspecs' : ws.serialize(None, objects, 'application/json')}
    return render(request, 'index.html', context)
