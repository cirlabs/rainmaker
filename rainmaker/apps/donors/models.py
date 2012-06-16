from __future__ import division
from django.db import models
from django.db.models import Sum
from django.contrib.localflavor.us.models import USStateField
from utils.competition_rank import competition_rank


########## CUSTOM MANAGERS ##########

class GroupManager(models.Manager):
    def get_query_set(self):
        return super(GroupManager, self).get_query_set().filter(published=True, type='C')

class IndividualManager(models.Manager):
    def get_query_set(self):
        return super(IndividualManager, self).get_query_set().filter(published=True, type='I')

class PublishedManager(models.Manager):
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

########## BASE MODELS AND ABSTRACT CLASSES (DON'T MESS WITH THESE) ##########

class DonorBase(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    type = models.CharField(max_length=1, choices=(('C', 'Group'), ('I', 'Individual')), db_index=True)
    location = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    location_city = models.CharField(max_length=255, blank=True)
    location_state = USStateField(blank=True)
    line_of_work = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='donors', blank=True)
    image_credit = models.CharField(max_length=255, blank=True)
    image_credit_url = models.URLField(max_length=255, blank=True)
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
    published_objects = PublishedManager()

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
    def wins_money(self):
        output = self.relatedcontribution_set.filter(contribution__new_contest_result='W').aggregate(Sum('contribution__amount'))['contribution__amount__sum']
        if not output:
            output = 0
        return output

    @property
    def losses_money(self):
        output = self.relatedcontribution_set.filter(contribution__new_contest_result='L').aggregate(Sum('contribution__amount'))['contribution__amount__sum']
        if not output:
            output = 0
        return output

    @property
    def win_pct(self):
        wins = self.wins_money
        losses = self.losses_money
        
        try:
            return '{0:.0f} percent'.format((wins / (wins + losses)) * 100)
        except ZeroDivisionError:
            return "N/A"

    @property
    def cand_contrib_count(self):
        count = self.relatedcontribution_set.filter(contribution__recipient_type='P').count()
        return count
        
    @property
    def ballot_contrib_count(self):
        count = self.relatedcontribution_set.filter(contribution__related_proposition__isnull=False).count()
        return count

    @property
    def party_contrib_count(self):
        count = self.relatedcontribution_set.exclude(contribution__related_proposition__isnull=False).filter(contribution__recipient_type='C').count()
        return count

    @property
    def donor_rank(self):
        #check if group or individual
        rank_list = self.__class__.published_objects.filter(type=self.type)
        rank = competition_rank(rank_list, self, 'contribs_sum', direction='desc')
        return rank

    def get_party_pct(self, p):
        count = self.relatedcontribution_set.all().count()
        party_count = self.relatedcontribution_set.filter(contribution__recipient_party=p).count()
        return party_count / count

    @property
    def dominant_party(self):
        import operator
        results = {}
        party_choices = ['R', 'D', 'I']
        for choice in party_choices:
            results[choice] = self.relatedcontribution_set.filter(contribution__recipient_party=choice).count()
        return max(results.iteritems(), key=operator.itemgetter(1))[0]


class BadgeBase(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    image = models.ImageField(upload_to='badges', null=True, blank=True)
    short_description = models.TextField(max_length=255, blank=True)
    long_description = models.TextField(max_length=255, blank=True)
    sort_order = models.IntegerField(null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('badge_detail', (), {'slug': self.slug})
        
    @property
    def donor_count(self):
        return self.donor_set.count()


########## CHILD CLASSES AND CONCRETE MODELS (MESS WITH THESE) ##########

class Donor(DonorBase):
    pass
        

class Badge(BadgeBase):
    pass


class RelatedDonor(models.Model):
    donor = models.ForeignKey(Donor, related_name='orig_donor')
    related_donor = models.ForeignKey(Donor)

    def __unicode__(self):
        return repr(self.related_donor)

    def save(self, *args, **kwargs):
        """
        Reassigns related contributions when a RelatedDonor is added.
        """
        super(RelatedDonor, self).save(*args, **kwargs)
        for rc in self.related_donor.relatedcontribution_set.all():
            self.donor.relatedcontribution_set.add(rc)
        # TODO: RESET DONOR SUM, COUNT
        self.donor.save()

    def delete(self, *args, **kwargs):
        """
        Assigns related contributions back to original donor when RelatedDonor is deleted.
        """
        for rc in self.donor.relatedcontribution_set.filter(contribution__donor_name=self.related_donor.name):
            self.related_donor.relatedcontribution_set.add(rc)
        self.related_donor.save()
        super(RelatedDonor, self).delete(*args, **kwargs)
