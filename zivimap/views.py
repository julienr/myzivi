from django.shortcuts import render
from django.core import serializers
from zivimap.models import WorkSpec

def index(request):
    ws = WorkSpec.objects.all()[:10]
    sws = serializers.serialize('json', ws)
    context = {'workspecs' : sws}
    return render(request, 'index.html', context)
