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

    def __unicode__(self):
        return u"[%s] %s" % (self.phid, self.shortname)
