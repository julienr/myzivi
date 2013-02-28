from django.db import models
from django.utils.translation import ugettext_lazy as _

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
            (u'health' , _('Health')), (u'social' , _('Social')),
            (u'culture' , _('Culture')), (u'nature' , _('Nature protection')),
            (u'forest' , _('Forest work')), (u'agriculture' , _('Agriculture')),
            (u'dev_cooperation' , _('Development & cooperation')),
            (u'disaster_help' , _('Disasters help'))
    )
    activity_domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)

    LANG_CHOICES = (
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
    )
    language = models.CharField(max_length=20, choices=LANG_CHOICES)

    def __unicode__(self):
        return u"[%s] %s" % (self.phid, self.shortname)

class DateRange(models.Model):
    workspec = models.ForeignKey(WorkSpec)
    start = models.DateField(db_index=True)
    end = models.DateField(db_index=True)
