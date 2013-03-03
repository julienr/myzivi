from django.shortcuts import render, redirect
from django.core import serializers
from django import forms
from zivimap.api import *
from zivimap.models import Address, WorkSpec, DateRange
from django.db.models import Q
from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
import json
from datetime import datetime

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
    date_range = forms.CharField(required=False,
            widget=forms.TextInput(attrs={'class':'daterange',
                #'readonly':'readonly'
                }),
            label=_('Date range'))

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
    date_range = cd['date_range']
    if len(date_range) > 0:
        start_date, end_date = date_range.split('-')
        start_date = datetime.strptime(start_date.strip(), '%d/%m/%Y').date()
        end_date = datetime.strptime(end_date.strip(), '%d/%m/%Y').date()
        Qfilters &= Q(daterange__start__gte=start_date)
        Qfilters &= Q(daterange__end__lte=end_date)
    return Qfilters


def sitemap(request):
    return render(request, 'sitemap.xml')

def index(request):
    # Save current language in session (in case the user used a i18n url)
    lang = translation.get_language()
    request.session['django_language'] = lang

    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        addresses = all_resources(request, AddressResource(),
                                  Address.objects.all())
        Qws = build_workspecs_filter(form)
        wsq = WorkSpec.objects.filter(Qws)
        ws = all_resources(request, MapSearchResource(), wsq)
        first_time_message = not request.session.get('visited', False)
        request.session['visited'] = True
        date_min, date_max = DateRange.get_min_max()
        context = {'addresses': addresses,
                   'workspecs' : ws,
                   'search_form' : form,
                   'daterange_min' : date_min,
                   'daterange_max' : date_max,
                   'first_time_message' : first_time_message}
        return render(request, 'index.html', context)
    else:
        return redirect('index')


