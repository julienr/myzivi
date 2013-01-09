from django.shortcuts import render
from django.core import serializers
from zivimap.models import WorkSpec
import json

def index(request):
    workspecs = WorkSpec.objects.all()[:10]
    sws = serializers.serialize('json', workspecs, relations=('address',))
    context = {'workspecs' : sws}
    return render(request, 'index.html', context)
