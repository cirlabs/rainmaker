from __future__ import division
from django.db import models
from django.db.models import Sum
from django.contrib.localflavor.us.models import USStateField
from utils.competition_rank import competition_rank


########## CUSTOM MANAGERS ##########

class GroupManager(models.Manager):
    """
    Returns published group donors.
    """
    def get_query_set(self):
        return super(GroupManager, self).get_query_set().filter(published=True, type='C').order_by('-contribs_sum')

class IndividualManager(models.Manager):
    """
    Returns published individual donors.
    """
    def get_query_set(self):
        return super(IndividualManager, self).get_query_set().filter(published=True, type='I').order_by('-contribs_sum')

class PublishedManager(models.Manager):
    """
    Returns all published donors.
    """
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

########## BASE MODELS AND ABSTRACT CLASSES (DON'T MESS WITH THESE) ##########

class DonorBase(models.Model):
    """
    Abstract base model to represent core attributes of Donor objects.
    """
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True,
        help_text="Don't change this unless you know what you're doing")
    type = models.CharField(max_length=1, choices=(('C', 'Group'), ('I', 'Individual')), db_index=True)
    bio = models.TextField(blank=True,
        help_text="A short biography of the donor. Will show up on donor detail pages.")
    location_city = models.CharField(max_length=255, blank=True,
        help_text="Donor's headquarters or primary place of residence.")
    location_state = USStateField(blank=True)
    line_of_work = models.CharField(max_length=255, blank=True,
        help_text="Brief description of the donor's industry or occupation.")
    image = models.ImageField(upload_to='donors', blank=True,
        help_text='Mug shot or other image of the donor. Optional.')
    image_credit = models.CharField(max_length=255, blank=True)
    image_credit_url = models.URLField(max_length=255, blank=True)
    contribs_sum = models.FloatField('Sum of contributions', blank=True, null=True)
    contribs_count = models.IntegerField('Count of contributions', blank=True, null=True)
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
    def donor_rank(self):
        """
        Returns the donor's rank number. Calculated dynamically. Could be recalculated
        on object save to cut down on a healthy bit of processing time, but it seems to
        work fine as-is for now.
        """
        # Only display ranks from the top 50 to cut down on massive requests. It's
        # a cheap solution, but the site won't load if we don't limit the number.
        rank_list = self.__class__.published_objects.filter(type=self.type)[:50]
        rank = competition_rank(rank_list, self, 'contribs_sum', direction='desc')
        return rank

    @property
    def wins_money(self):
        """
        Returns the amount of money spent by a donor on winning candidates and
        ballot measure committees.
        """
        from apps.props.models import RelatedCommittee
        contest_wins = self.relatedcontribution_set.filter(
            contribution__new_contest_result='W').aggregate(
                Sum('contribution__amount'))['contribution__amount__sum']
        if not contest_wins: contest_wins = 0.0

        ballot_wins = 0.0
        for rc in self.relatedcontribution_set.filter(contribution__related_proposition__isnull=False):
            try:
                prop_donor = RelatedCommittee.objects.get(
                    proposition__contribution=rc.contribution, donor=rc.donor)
            except RelatedCommittee.DoesNotExist:
                continue
            if rc.contribution.related_proposition.result == 'P':
                 if prop_donor.position == 'F':
                    ballot_wins += rc.contribution.amount
            elif rc.contribution.related_proposition.result == 'F':
                if prop_donor.position == 'A':
                    ballot_wins += rc.contribution.amount
        return contest_wins + ballot_wins

    @property
    def losses_money(self):
        """
        Returns the amount of money spent by a donor on losing candidates and
        ballot measure committees.
        """
        from apps.props.models import RelatedCommittee
        contest_losses = self.relatedcontribution_set.filter(
            contribution__new_contest_result='L').aggregate(
                Sum('contribution__amount'))['contribution__amount__sum']
        if not contest_losses: contest_losses = 0.0

        ballot_losses = 0.0
        for rc in self.relatedcontribution_set.filter(contribution__related_proposition__isnull=False):
            try:
                prop_donor = RelatedCommittee.objects.get(
                    proposition__contribution=rc.contribution, donor=rc.donor)
            except RelatedCommittee.DoesNotExist:
                continue
            if rc.contribution.related_proposition.result == 'P':
                 if prop_donor.position == 'A':
                    ballot_losses += rc.contribution.amount
            elif rc.contribution.related_proposition.result == 'F':
                if prop_donor.position == 'P':
                    ballot_losses += rc.contribution.amount
        return contest_losses + ballot_losses

    @property
    def win_pct(self):
        """
        Calculates the percentage of a donor's money spent on winning candidates.
        """
        wins = self.wins_money
        losses = self.losses_money
        try:
            return '{0:.0f} percent'.format((wins / (wins + losses)) * 100)
        except ZeroDivisionError:
            return "N/A"

    @property
    def cand_contrib_count(self):
        """
        Returns a count of the number of contributions a donor gave to candidates.
        """
        count = self.relatedcontribution_set.filter(contribution__recipient_type='P').count()
        return count

    @property
    def cmte_contrib_count(self):
        """
        Returns a count of the number of contributions a donor gave to committees, such as
        parties and ballot measures.
        """
        count = self.relatedcontribution_set.filter(contribution__recipient_type='C').count()
        return count        

    @property
    def ballot_contrib_count(self):
        """
        Returns a count of the number of contributions a donor gave specifically to ballot measures.
        """
        count = self.relatedcontribution_set.filter(contribution__related_proposition__isnull=False).count()
        return count


class BadgeBase(models.Model):
    """
    Abstract base model representing donor badges.
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    image = models.ImageField(upload_to='badges', null=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True,
        help_text='A brief one-sentence description of the badge.')
    long_description = models.TextField(blank=True,
        help_text='A longer, more detailed description of the badge and its criteria.')
    sort_order = models.IntegerField(null=True,
        help_text='The order you want the badge to appear on the list view page.')
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['name',]

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('badge_detail', (), {'slug': self.slug})
        
    @property
    def donor_count(self):
        """
        Returns the number of donors who have been assigned a given badge.
        """
        return self.donor_set.count()


########## CHILD CLASSES AND CONCRETE MODELS (MESS WITH THESE) ##########

class Donor(DonorBase):
    """
    Concrete donor model. Make and changes or additions here.
    """
    pass
        

class Badge(BadgeBase):
    """
    Concrete badge model. Make any changes or additions here.
    """
    pass


class RelatedDonor(models.Model):
    """
    Concrete model representing related donors. The concept of related donors is that
    in a campaign finance database, even one as well-standardized as NIMSP's, a donor
    might be represented by several names. For example, a single donor might be represented
    in the database as "SEIU" and "Service Employees International Union."

    This model serves as a bridge to relate donors that should be represented under the same
    name but are improperly standardized in the dataset. Basically, it lets users in the admin
    interface lump together the contributions of multiple donors into one.
    """
    donor = models.ForeignKey(Donor, related_name='orig_donor')
    related_donor = models.ForeignKey(Donor)

    def __unicode__(self):
        return repr(self.related_donor)

    def reset_totals(self):
        """
        Resets donor count and sum totals based on changes to related donors.
        """
        # Reset counts
        self.donor.contribs_count = self.donor.relatedcontribution_set.all().count()
        self.related_donor.contribs_count = self.related_donor.relatedcontribution_set.all().count()

        # Reset sums
        donor_sum = self.donor.relatedcontribution_set.all().aggregate(
            Sum('contribution__amount'))['contribution__amount__sum']
        if not donor_sum:
            donor_sum = 0

        related_donor_sum = self.related_donor.relatedcontribution_set.all().aggregate(
            Sum('contribution__amount'))['contribution__amount__sum']
        if not related_donor_sum:
            related_donor_sum = 0

        self.donor.contribs_sum = donor_sum
        self.related_donor.contribs_sum = related_donor_sum
        return

    def save(self, *args, **kwargs):
        """
        Reassigns related contributions to the original donor from the related donor.
        Also recalculates all counts and totals.
        """
        super(RelatedDonor, self).save(*args, **kwargs)
        for rc in self.related_donor.relatedcontribution_set.all():
            self.donor.relatedcontribution_set.add(rc)
        self.reset_totals()
        self.related_donor.save()
        self.donor.save()
        return

    def delete(self, *args, **kwargs):
        """
        Assigns related contributions back to the original donor if a related donor is deleted.
        """
        for rc in self.donor.relatedcontribution_set.filter(contribution__donor_name=self.related_donor.name):
            self.related_donor.relatedcontribution_set.add(rc)
        self.reset_totals()
        self.related_donor.save()
        self.donor.save()
        super(RelatedDonor, self).delete(*args, **kwargs)
        return