from django.db import models
from apps.donors.models import Donor

########## BASE MODELS AND ABSTRACT CLASSES (DON'T MESS WITH THESE) ##########

class PropositionBase(models.Model):
    """
    Abstract base class representing ballot measures.
    """
    cycle = models.IntegerField('Election cycle', null=True)
    title = models.CharField(blank=True, max_length=100)
    number = models.CharField(blank=True, max_length=4)
    subject = models.CharField(blank=True, max_length=100)
    description = models.CharField(blank=True, max_length=255)
    result = models.CharField(max_length=1, choices=(('P', 'Passed'), ('F', 'Failed')))
    ext_link = models.URLField(null=True, blank=True, max_length=255)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


########## CHILD CLASSES AND CONCRETE MODELS (MESS WITH THESE) ##########

class Proposition(PropositionBase):
    """
    Concrete class representing ballot measures. Make and changes or additions here.
    """
    pass


class RelatedCommittee(models.Model):
    """
    RelatedCommittee is an intermediary model that allows the user to relate a donor
    with a proposition, along with a position. For example, it lets a user create the
    relationship that the SEIU is for/against Prop. 99.

    Assigning these relationships enables certain visualizations and calculations related
    to ballot measures. However, these assignments are optional.
    """
    proposition = models.ForeignKey(Proposition, db_index=True)
    donor = models.ForeignKey(Donor, db_index=True)
    position = models.CharField(max_length=1, choices=(('F', 'For'), ('A', 'Against')))

    def __unicode__(self):
        return '%s: %s -> %s' % (self.position, self.donor, self.proposition)