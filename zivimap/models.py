from django.db import models

class WorkSpec(models.Model):
    phid = models.CharField(max_length=40, primary_key=True)
    shortname = models.CharField(max_length=80)
    url = models.TextField()
    # TODO: address
