from zivimap.models import WorkSpec
from tastypie.resources import ModelResource

class WorkSpecResource(ModelResource):
    class Meta:
        queryset = WorkSpec.objects.all()
        resource_name = 'workspec'
