from zivimap.models import WorkSpec
from django.db.models import Max

def add_stats(request):
    """Context processor that add some statistics about the DB"""
    last_update = WorkSpec.objects.aggregate(Max('modified'))['modified__max']
    num_workspecs = WorkSpec.objects.count()
    return {'last_update' : last_update,
            'num_workspecs' : num_workspecs}
