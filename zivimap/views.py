from django.shortcuts import render, redirect
from django.core import serializers
from django import forms
from zivimap.api import *
from zivimap.models import Address, WorkSpec
from django.db.models import Q
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
import json

def all_resources(request, resource, queryset):
    objects = []
    for m in queryset:
        bundle = resource.build_bundle(obj=m, request=request)
        bundle = resource.full_dehydrate(bundle)
        objects.append(bundle)
    return resource.serialize(None, objects, 'application/json')

class SearchForm(forms.Form):
    domains = forms.MultipleChoiceField(required=False,
            choices=WorkSpec.DOMAIN_CHOICES,
            widget=forms.CheckboxSelectMultiple,
            label=_('Domains'))
    languages = forms.MultipleChoiceField(required=False,
            choices=WorkSpec.LANG_CHOICES,
            widget=forms.CheckboxSelectMultiple,
            label=_('Languages'))

def build_workspecs_filter(search_form):
    """Return a filter dict based on SearchForm cleaned_data"""
    assert search_form.is_valid()
    cd = search_form.cleaned_data
    Qfilters = Q()
    domains = cd['domains']
    if len(domains) > 0:
        Qfilters &= Q(activity_domain__in=domains)
    languages = cd['languages']
    if len(languages) > 0:
        Qfilters &= Q(language__in=languages)
    return Qfilters


def index(request):
    # Save current language in session (in case the user used a i18n url)
    lang = translation.get_language()
    request.session['django_language'] = lang

    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        domains = cd['domains']
        addresses = all_resources(request, AddressResource(),
                                  Address.objects.all())
        Qws = build_workspecs_filter(form)
        wsq = WorkSpec.objects.filter(Qws)
        ws = all_resources(request, MapSearchResource(), wsq)
        first_time_message = not request.session.get('visited', False)
        request.session['visited'] = True
        context = {'addresses': addresses,
                   'workspecs' : ws,
                   'search_form' : form,
                   'first_time_message' : first_time_message}
        return render(request, 'index.html', context)
    else:
        return redirect('index')
