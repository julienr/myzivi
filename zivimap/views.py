from django.shortcuts import render, redirect
from django.core import serializers
from django import forms
from zivimap.api import *
from zivimap.models import Address, WorkSpec
import json

def all_resources(request, resource, queryset):
    objects = []
    for m in queryset:
        bundle = resource.build_bundle(obj=m, request=request)
        bundle = resource.full_dehydrate(bundle)
        objects.append(bundle)
    return resource.serialize(None, objects, 'application/json')

#def index(request):
    #addresses = all_resources(request, AddressResource(), Address.objects.all())
    #ws = all_resources(request, MapSearchResource(), WorkSpec.objects.all())
    #context = {'addresses': addresses,
               #'workspecs' : ws}
    #return render(request, 'index.html', context)

def index(request):
    form = SearchForm()
    context = {'search_form' : form}
    return render(request, 'index.html', context)


class SearchForm(forms.Form):
    domains = forms.MultipleChoiceField(required=False, choices=WorkSpec.DOMAIN_CHOICES,
            widget=forms.CheckboxSelectMultiple)

def search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        domains = cd['domains']
        addresses = all_resources(request, AddressResource(),
                                  Address.objects.all())
        if len(domains) == 0:
            wsq = WorkSpec.objects.all()
        else:
            wsq = WorkSpec.objects.filter(activity_domain__in=domains)
        ws = all_resources(request, MapSearchResource(), wsq)
        context = {'addresses': addresses,
                   'workspecs' : ws,
                   'search_form' : form}
        return render(request, 'index.html', context)
    else:
        return redirect('index')


