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
    start_min = forms.DateField(required=False,
            input_formats=['%d.%m.%Y'],
            widget=forms.DateInput(attrs={'class':'datepicker'}),
            label=_('Earliest start (dd.mm.YY)'))
    end_max = forms.DateField(required=False,
            input_formats=['%d.%m.%Y'],
            widget=forms.DateInput(attrs={'class':'datepicker'}),
            label=_('Latest end (dd.mm.YY)'))
    #date_range = forms.CharField(required=False,
            #widget=forms.TextInput(attrs={'class':'daterange',
                ##'readonly':'readonly'
                #}),
            #label=_('Date range'))

def search_workspecs(search_form):
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
    #date_range = cd['date_range']
    #if len(date_range) > 0:
        #start_date, end_date = date_range.split('-')
        #start_date = datetime.strptime(start_date.strip(), '%d/%m/%Y').date()
        #end_date = datetime.strptime(end_date.strip(), '%d/%m/%Y').date()
        #ranges = DateRange.objects.filter(start__gte=start_date,
                                          #end__lte=end_date)
        #ranges = ranges.values('workspec_id').annotate()

        ## ID of workspecs that don't have a daterange
        #no_ranges = WorkSpec.objects.annotate(rc=Count('daterange')).filter(rc=0).values('phid').annotate()
        #Qfilters &= Q(phid__in=ranges) | Q(phid__in=no_ranges)

    # Need an order by here, otherwise, the clustering will change based
    # on the ordering of the WorkSpec set, which might be confusing (like
    # when searching without date range and with the whole date range)
    return WorkSpec.objects.filter(Qfilters).order_by('phid')

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
        wsq = search_workspecs(form)
        ws = all_resources(request, WorkSpecSearchResource(), wsq)
        first_time_message = not request.session.get('visited', False)
        request.session['visited'] = True
        date_min, date_max = DateRange.get_min_max()
        context = {'addresses': addresses,
                   'workspecs' : ws,
                   'search_form' : form,
                   'daterange_min' : date_min,
                   'daterange_max' : date_max,
                   'first_time_message' : first_time_message}

        workspec_search_url = reverse('api_dispatch_list', kwargs={
            'api_name': 'v1',
            'resource_name': 'workspec_search'})
        query = MultiValueDict()
        query['format'] = json
        for lang in cd['languages']:
            query.appendlist('language__in', lang)
        for dom in cd['domains']:
            query.appendlist('activity_domain__in', dom)

        workspec_search_url += urlencode(query, doseq=True)
        print workspec_search_url

        return render(request, 'index.html', context)
    else:
        return redirect('index')


