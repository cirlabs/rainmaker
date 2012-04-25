from django.db import models
from apps.donors.models import Donor


class Catcode(models.Model):
    source = models.CharField(max_length=255)
    code = models.CharField(primary_key=True, max_length=10, db_index=True)
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    order = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Contribution(models.Model):
    cycle = models.IntegerField(db_index=True)
    transaction_namespace = models.CharField(max_length=255, blank=True)
    transaction_id = models.CharField(max_length=255, db_index=True)
    transaction_type = models.CharField(max_length=255, blank=True)
    filing_id = models.CharField(max_length=255, blank=True)
    is_amendment = models.CharField(max_length=255, blank=True)
    amount = models.FloatField(blank=True, null=True, db_index=True)
    date = models.DateField(blank=True, null=True, db_index=True)
    contributor_name = models.CharField(max_length=255, blank=True, db_index=True)
    contributor_ext_id = models.IntegerField(blank=True, null=True)
    contributor_type = models.CharField(max_length=255, blank=True)
    contributor_occupation = models.CharField(max_length=255, blank=True)
    contributor_employer = models.CharField(max_length=255, blank=True)
    contributor_gender = models.CharField(max_length=255, blank=True)
    contributor_address = models.CharField(max_length=255, blank=True)
    contributor_city = models.CharField(max_length=255, blank=True)
    contributor_state = models.CharField(max_length=255, blank=True)
    contributor_zipcode = models.CharField(max_length=25, blank=True)
    contributor_category = models.ForeignKey(Catcode, db_column='contributor_category', blank=True, null=True, db_index=True)
    organization_name = models.CharField(max_length=255, blank=True, db_index=True)
    organization_ext_id = models.IntegerField(blank=True, null=True)
    parent_organization_name = models.CharField(max_length=255, blank=True, db_index=True)
    parent_organization_ext_id = models.IntegerField(blank=True, null=True)
    recipient_name = models.CharField(max_length=255, blank=True, db_index=True)
    recipient_ext_id = models.IntegerField(blank=True, null=True)
    recipient_party = models.CharField(max_length=255,blank=True)
    recipient_type = models.CharField(max_length=255, blank=True)
    recipient_state = models.CharField(max_length=255, blank=True)
    recipient_state_held = models.CharField(max_length=255, blank=True)
    recipient_category = models.CharField(max_length=255, blank=True)
    committee_name = models.CharField(max_length=255, blank=True)
    committee_ext_id = models.IntegerField(blank=True, null=True)
    committee_party = models.CharField(max_length=255, blank=True)
    candidacy_status = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=255, blank=True)
    district_held = models.CharField(max_length=255, blank=True)
    seat = models.CharField(max_length=255, blank=True)
    seat_held = models.CharField(max_length=255)
    seat_status = models.CharField(max_length=255, blank=True)
    seat_result = models.CharField(max_length=255, blank=True, db_index=True)

    class Meta:
        ordering = ('-date',)

    def __unicode__(self):
        return '$%s contribution from %s to %s in %s' % (self.amount,
            self.contributor_name, self.recipient_name, self.date.year)

    @models.permalink
    def get_absolute_url(self):
        return ('contribution_detail', (), {'pk': self.id})


class RelatedContribution(models.Model):
    contribution = models.ForeignKey(Contribution, db_index=True)
    donor = models.ForeignKey(Donor, db_index=True)

    class Meta:
        ordering = ('-contribution__amount',)

    def __unicode__(self):
        return repr(self.contribution)