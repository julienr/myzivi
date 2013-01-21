from django.db import models

class Address(models.Model):
    canton = models.CharField(max_length=50)
    locality = models.CharField(max_length=80)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __unicode__(self):
        return self.locality + u", " + self.canton

class WorkSpec(models.Model):
    # phid with the dots removed
    phid = models.CharField(max_length=40, primary_key=True)
    # raw phid as found on website (includes dot)
    raw_phid = models.CharField(max_length=40)
    shortname = models.CharField(max_length=80)
    url = models.URLField()
    address = models.ForeignKey(Address)
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)

    # Additional data from webpage
    institution_name = models.TextField()
    institution_description = models.TextField()
    job_title = models.TextField()
    job_functions = models.TextField()
    DOMAIN_CHOICES = (
            (u'health' , u'Health'), (u'social' , u'Social'),
            (u'culture' , u'Culture'), (u'nature' , u'Nature protection'),
            (u'forest' , u'Forest work'), (u'agriculture' , u'Agriculture'),
            (u'dev_cooperation' , u'Development & cooperation'),
            (u'disaster_help' , u'Disasters help')
    )
    activity_domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    # TODO: Handle multiple start/end dates

    def __unicode__(self):
        return u"[%s] %s" % (self.phid, self.shortname)
