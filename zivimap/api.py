import ziviweb.settings as settings
from django.core.urlresolvers import reverse
from zivimap.models import WorkSpec, Address, DateRange
from django.db.models import Q, Count
from tastypie.resources import ModelResource, Resource, Bundle, ALL
from tastypie import fields, utils
from datetime import datetime

class AddressResource(ModelResource):
    class Meta:
        queryset = Address.objects.all()
        resource_name = 'address'
        include_resource_uri = False
        limit = 0

class WorkSpecSearchResource(ModelResource):
    """
    This is a specialized resource that returns a list of workspecs for a given
    query. The workspecs description is shortened to only a few fields to
    reduce response size
    """
    class Meta:
        queryset = WorkSpec.objects.all()
        resource_name = 'workspec_search'
        allowed_methods = ['get']
        include_resource_uri = False
        # Without that, resource_uri is empty in the view
        api_name = settings.API_VERSION
        limit = 0
        max_limit = 0
        fields = ['address_id', 'shortname', 'raw_phid', 'phid']
        filtering = {
            'activity_domain': ('in',),
            'language': ('in',),
        }

    def dehydrate(self, bundle):
        bundle.data['addrid'] = bundle.obj.address_id
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(WorkSpecSearchResource, self).build_filters(filters)
        # By default, tastypie doesn't allow to filter on fields that are
        # not in Meta.fields. Overwrite this
        lang_filters = filters.getlist('language__in')
        if lang_filters:
            orm_filters['language__in'] = lang_filters
        domain_filters = filters.getlist('activity_domain__in')
        if domain_filters:
            orm_filters['activity_domain__in'] = domain_filters
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        res = super(WorkSpecSearchResource, self).apply_filters(request,
                applicable_filters)
        # Handle complex filters here
        start_min = request.GET.get('start_min', None)
        end_max = request.GET.get('end_max', None)
        if start_min is not None or end_max is not None:
            drfilters = Q()
            if start_min is not None:
                start_date = datetime.strptime(start_min.strip(),
                                               '%Y-%m-%d').date()
                drfilters &= Q(start__gte=start_date)
            if end_max is not None:
                end_date = datetime.strptime(end_max.strip(),
                                             '%Y-%m-%d').date()
                drfilters &= Q(end__lte=end_date)
            ranges = DateRange.objects.filter(drfilters).values('workspec_id')\
                                                        .annotate()
            # ID of workspecs that don't have a daterange
            # TODO: This should be merged in the subsequent workspec query
            no_ranges = WorkSpec.objects.annotate(rc=Count('daterange'))\
                                .filter(rc=0).values('phid').annotate()
            res = res.filter(Q(phid__in=ranges) | Q(phid__in=no_ranges))
        return res


class WorkSpecResource(ModelResource):
    address = fields.ToOneField(AddressResource, 'address', full=True)
    class Meta:
        queryset = WorkSpec.objects.select_related().all()
        resource_name = 'workspec'
        allowed_methods = ['get']
        # Without that, resource_uri is empty in the view
        api_name = settings.API_VERSION
        limit = 20

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(WorkSpecResource, self).build_filters(filters)

        # We accept a "latlngbb=47.365,8.783,47.367,8.785" parameter
        # specifying a latlng bounding box (as the one returned by google maps
        # getBounds())
        if 'latlngbb' in filters:
            latlngbb = filters['latlngbb']
            swlat, swlng, nelat, nelng = map(float, latlngbb.split(','))

            assert swlat < nelat
            assert swlng < nelng
            orm_filters['address__latitude__range'] = (swlat, nelat)
            orm_filters['address__longitude__range'] = (swlng, nelng)

        return orm_filters
