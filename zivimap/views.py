from django.shortcuts import render
import json

DATAFILE = '/home/julien/dev/zivi/_data/scraped/final_items.json'
with open(DATAFILE) as f:
    items = json.load(f)

def index(request):
    context = {'items' : json.dumps(items)}
    return render(request, 'index.html', context)
