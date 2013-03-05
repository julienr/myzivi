from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core import serializers
from django import forms
from zivimap.api import *
from zivimap.models import Address, WorkSpec, DateRange
from django.db.models import Q, Count
from django.conf import settings
from django.utils.http import urlencode
from django.utils.datastructures import MultiValueDict
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
import json
from zivimap.forms import SelectMonthYearWidget
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
    def __init__(self, date_min, date_max, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        years = range(date_min.year, date_max.year + 1)
        self.fields.update({
            'start_min': forms.DateField(required=False,
                input_formats=['%d.%m.%Y'],
                widget=SelectMonthYearWidget(date_min, day='first', years=years),
                label=_('Earliest start')),
            'end_max': forms.DateField(required=False,
                input_formats=['%d.%m.%Y'],
                widget=SelectMonthYearWidget(date_max, day='last', years=years),
                label=_('Latest end'))
            })

def sitemap(request):
    return render(request, 'sitemap.xml')

def index(request):
    # Save current language in session (in case the user used a i18n url)
    lang = translation.get_language()
    request.session['django_language'] = lang

    date_min, date_max = DateRange.get_min_max()
    form = SearchForm(date_min, date_max, request.GET)
    if form.is_valid():
        cd = form.cleaned_data

        first_time_message = not request.session.get('visited', False)
        request.session['visited'] = True

        workspec_search_url = reverse('api_dispatch_list', kwargs={
            'api_name': 'v1',
            'resource_name': 'workspec_search'})
        query = MultiValueDict()
        query['format'] = 'json'
        for lang in cd['languages']:
            query.appendlist('language__in', lang)
        for dom in cd['domains']:
            query.appendlist('activity_domain__in', dom)
        start_min = cd['start_min']
        end_max = cd['end_max']
        if start_min:
            query['start_min'] = start_min
        if end_max:
            query['end_max'] = end_max

        workspec_search_url += '?' + urlencode(query, doseq=True)
        address_url = reverse('api_dispatch_list', kwargs={
            'api_name': 'v1',
            'resource_name': 'address'})

        context = {'search_form' : form,
                   'first_time_message' : first_time_message,
                   'workspec_search_url' : workspec_search_url,
                   'address_url': address_url}

        return render(request, 'index.html', context)
    else:
        return redirect('index')


