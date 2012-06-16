from django.db import models
from apps.donors.models import Donor

class Proposition(models.Model):
    election_date = models.DateField(blank=True, null=True, db_index=True)
    cycle = models.IntegerField(null=True)
    title = models.CharField(blank=True, max_length=100)
    number = models.CharField(blank=True, max_length=50)
    subject = models.CharField(blank=True, max_length=100)
    description = models.CharField(blank=True, max_length=255)
    result = models.CharField(max_length=1, choices=(('P', 'Passed'), ('F', 'Failed')))
    ext_link = models.URLField(null=True, blank=True, max_length=255)

    def __unicode__(self):
        return self.title


class RelatedCommittee(models.Model):
    proposition = models.ForeignKey(Proposition, db_index=True)
    donor = models.ForeignKey(Donor, db_index=True)
    position = models.CharField(max_length=1, choices=(('F', 'For'), ('A', 'Against')))


    # Override save and delete to mark contributions properly