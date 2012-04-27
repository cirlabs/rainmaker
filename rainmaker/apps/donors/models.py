from __future__ import division
from django.db import models

########## CUSTOM MANAGERS ##########

class GroupManager(models.Manager):
    def get_query_set(self):
        return super(GroupManager, self).get_query_set().filter(published=True, type='C')

class IndividualManager(models.Manager):
    def get_query_set(self):
        return super(IndividualManager, self).get_query_set().filter(published=True, type='I')


########## BASE MODELS AND ABSTRACT CLASSES (DON'T MESS WITH THESE) ##########

class DonorBase(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    type = models.CharField(max_length=1, choices=(('Group', 'C'), ('Individual', 'I')), db_index=True)
    location = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='donors', blank=True)
    contribs_sum = models.FloatField(blank=True, null=True)
    contribs_count = models.IntegerField(blank=True, null=True)
    badges = models.ManyToManyField('Badge', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    # Managers
    objects = models.Manager()
    groups = GroupManager()
    individuals = IndividualManager()

    class Meta:
        ordering = ('-contribs_sum',)
        abstract = True

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('donor_detail', (), {'slug': self.slug})

    @property
    def wins(self):
        return self.relatedcontribution_set.filter(contribution__seat_result='W').count()

    @property
    def losses(self):
        return self.relatedcontribution_set.filter(contribution__seat_result='L').count()

    @property
    def win_pct(self):
        try:
            return '{0:.0f} percent'.format((self.wins / (self.wins + self.losses)) * 100)
        except ZeroDivisionError:
            return "N/A"


class BadgeBase(models.Model):
    name = models.CharField(max_length=50)
    art = models.ImageField(upload_to='badges')
    description = models.TextField(max_length=255)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


########## CHILD CLASSES AND CONCRETE MODELS (MESS WITH THESE) ##########

class Donor(DonorBase):
    pass


class Badge(BadgeBase):
    pass