from django.db import models
from django.db.models.signals import pre_delete
from apps.donors.models import Donor
from apps.props.models import Proposition, RelatedCommittee

########## BASE MODELS AND ABSTRACT CLASSES (DON'T MESS WITH THESE) ##########

class Catcode(models.Model):
    source = models.CharField(max_length=255)
    code = models.CharField(primary_key=True, max_length=10, db_index=True)
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    order = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class ContributionBase(models.Model):
    cycle = models.IntegerField(db_index=True)
    transaction_namespace = models.CharField(max_length=255, blank=True)
    transaction_id = models.CharField(max_length=255, db_index=True)
    transaction_type = models.CharField(max_length=255, blank=True)
    filing_id = models.CharField(max_length=255, blank=True)
    is_amendment = models.CharField(max_length=255, blank=True)
    amount = models.FloatField(blank=True, null=True, db_index=True)
    date = models.CharField(max_length=15, blank=True)
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
        abstract = True

    def __unicode__(self):
        return '$%s contribution from %s to %s in %s' % (self.amount,
            self.contributor_name, self.recipient_name, self.date.year)

    @models.permalink
    def get_absolute_url(self):
        return ('contribution_detail', (), {'pk': self.id})


########## CHILD CLASSES AND CONCRETE MODELS (MESS WITH THESE) ##########

class Contribution(ContributionBase):
    date_fixed = models.DateField(blank=True, null=True, db_index=True)
    donor_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    related_proposition = models.ForeignKey(Proposition, db_index=True, blank=True, null=True)
    new_contest_result = models.CharField(max_length=1, blank=True, null=True)

    def __unicode__(self):
        return '$%s contribution from %s to %s in %s' % (self.amount,
            self.donor_name, self.recipient_name, self.date_fixed.year)

    @property
    def is_ballot(self):
        is_ballot = False
        if self.related_proposition is not None:
            is_ballot = True
        return is_ballot


class RelatedContribution(models.Model):
    contribution = models.ForeignKey(Contribution, db_index=True)
    donor = models.ForeignKey(Donor, db_index=True)

    class Meta:
        ordering = ('-contribution__amount',)

    def __unicode__(self):
        return repr(self.contribution)

    @property
    def race_explainer(self):
        party_map = {
            'D': 'Democratic',
            'R': 'Republican',
            'I': 'Independent',
            'N': 'Nonpartisan',
            'U': 'Unknown',
        }
        
        output = []
        if self.bool_ballot == True:
            prop_donor = RelatedCommittee.objects.get(proposition__contribution=self.contribution, donor=self.donor)
            if prop_donor.position == 'F':
                supporting = 'Supporting '
            elif prop_donor.position == 'A':
                supporting = 'Opposing '
            else:
                supporting = ''
                
            if prop_donor.proposition.ext_link != '':
                link_start = ' <a href="%s" target="_blank">' % prop_donor.proposition.ext_link
                link_end = '</a>'
            else:
                link_start = ''
                link_end = ''
                
            explainer_text = '%s%sProposition %s%s' % (supporting, link_start, prop_donor.proposition.number, link_end)
            explainer = {'bool_winner': self.bool_winner, 'explainer_text': explainer_text, 'outcome_text': '(%s)' % prop_donor.proposition.get_result_display()}
            output.append(explainer)

        elif self.contribution.recipient_type == 'P':
            output = []
            output_str = ''
            output_str += party_map[self.contribution.recipient_party]
            output_str += ' candidate for '
            if self.contribution.seat == 'state:upper':
                output_str += 'upper house district '
                output_str += self.contribution.district.replace('CA-','')
            elif self.contribution.seat == 'state:lower':
                output_str += 'lower house district '
                output_str += self.contribution.district.replace('CA-','')
            elif self.contribution.seat == 'state:governor':
                output_str += 'governor/lieutenant governor'
            elif self.contribution.seat == 'state:office':
                output_str += 'statewide office'
            if self.contribution.seat == 'state:judicial':
                output_str += 'judicial office '
                
            if self.bool_winner == True:
                approved_text = '(Successful)'
            elif self.bool_winner == False:
                approved_text = '(Unsuccessful)'
            else:
                approved_text = ''
            
            explainer = {'bool_winner': self.bool_winner, 'explainer_text': output_str, 'outcome_text': approved_text}
            output.append(explainer)
        else:
            output = [] 
        return output

    @property
    def bool_ballot(self):
        if self.contribution.related_proposition is not None:
            return True
        else:
            return False

    @property
    def bool_candidate(self):
        if self.contribution.recipient_type == 'P':
            return True
        else:
            return False

    @property
    def bool_party(self):
        if self.contribution.recipient_type == 'C' and not self.contribution.is_ballot:
            return True
        else:
            return False

    @property
    def bool_loser(self):
        #necessary for differentiating losses and mixed results from missing results
        if self.bool_candidate:
            #candidate winner
            if self.contribution.seat_result != 'W':
                return True
            else:
                return False
                
        elif self.bool_ballot:
            #ballot initiatives
            bool_losses = False
            if self.contribution.related_proposition.result == 'F':
                bool_losses = True
            return bool_losses

        else:
            #no winners for party races
            return False
    
    @property
    def bool_mixedresult(self):
            return False
    
    @property
    def bool_winner(self):
        if self.bool_candidate:
            #candidate winner
            if self.contribution.seat_result == 'W':
                return True
            #candidate loser
            elif self.contribution.seat_result == 'L':
                return False
            else:
                return 'unknown'

        elif self.bool_ballot:
            #Check for cases with split results, send 'both' if found
            bool_wins = False
            if self.contribution.related_proposition.result == 'P':
                bool_wins = True
            return bool_wins
            #no winners for party races
        else:
            return False

    @property
    def outcome_text(self):
        if self.bool_candidate:
            if self.bool_winner:
                return 'Successful'
            else:
                return 'Unsuccessful'
        else:
            return ''

########## SIGNALS ##########

def delete_related(instance, **kwargs):
    rcs = RelatedContribution.objects.filter(donor__pk=instance.pk)
    rcs.delete()
    return

pre_delete.connect(delete_related, sender=Donor)
