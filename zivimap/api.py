import ziviweb.settings as settings
from django.core.urlresolvers import reverse
from zivimap.models import WorkSpec, Address
from tastypie.resources import ModelResource
from tastypie import fields, utils

class AddressResource(ModelResource):
    class Meta:
        queryset = Address.objects.all()
        resource_name = 'address'
        include_resource_uri = False

class WorkSpecResource(ModelResource):
    address = fields.ToOneField(AddressResource, 'address', full=True)
    class Meta:
        queryset = WorkSpec.objects.all()
        resource_name = 'workspec'
        allowed_methods = ['get']
        # Without that, resource_uri is empty in the view
        api_name = settings.API_VERSION
        limit = 0

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
