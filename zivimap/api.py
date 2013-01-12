import ziviweb.settings as settings
from django.core.urlresolvers import reverse
from zivimap.models import WorkSpec, Address
from tastypie.resources import ModelResource, Resource, Bundle
from tastypie import fields, utils

class AddressResource(ModelResource):
    class Meta:
        queryset = Address.objects.all()
        resource_name = 'address'
        include_resource_uri = False
        limit = 0

class MapSearchResource(ModelResource):
    """
    This is a specialized resource that returns a list of workspecs for a given
    query. The workspecs description is shortened to only a few fields to
    save bandwidth.
    """
    class Meta:
        queryset = WorkSpec.objects.all()
        resource_name = 'search'
        allowed_methods = ['get']
        include_resource_uri = True
        # Without that, resource_uri is empty in the view
        api_name = settings.API_VERSION
        limit = 0
        fields = ['address_id', 'shortname']

    def get_resource_uri(self, bundle_or_obj=None):
        # Same as ModelResource.get_resource_uri, but force resource name
        # to be workspec instead of search
        kwargs = {
            'resource_name': 'workspec'
        }
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.pk
        else:
            kwargs['pk'] = bundle_or_obj.id

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs=kwargs)

    def dehydrate(self, bundle):
        bundle.data['addrid'] = bundle.obj.address_id
        return bundle

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(MapSearchResource, self).build_filters(filters)

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
