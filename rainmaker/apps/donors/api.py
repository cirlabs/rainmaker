from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from apps.donors.models import Donor, Badge
from apps.contributions.models import Contribution, RelatedContribution

full_url_prefix = '/'

class DonorResource(ModelResource):
    badges = fields.ToManyField('apps.donors.api.BadgeResource', 'badges', full=True)
    
    class Meta:
        queryset = Donor.objects.filter(published=True)
        resource_name = 'donor'
        excludes = ['published','date_added','contribs_count','location','title']
        filtering = {
            'type': ALL,
        }
    
    def dehydrate(self, bundle):
        badge_list = []

        bundle.data['type'] = bundle.obj.get_type_display()
        bundle.data['image_source'] = bundle.obj.get_image_source_display()
        bundle.data['rank'] = bundle.obj.donor_rank
        bundle.data['wins_money'] = bundle.obj.wins_money
        bundle.data['losses_money'] = bundle.obj.losses_money
        bundle.data['win_percentage'] = bundle.obj.win_pct
        
        bundle.data['total_contributions_count'] = bundle.obj.contribs_count
        bundle.data['candidate_contributions_count'] = bundle.obj.cand_contrib_count
        bundle.data['committee_contributions_count'] = bundle.obj.cmte_contrib_count
        bundle.data['ballot_contributions_count'] = bundle.obj.ballot_contrib_count
        
        bundle.data['full_url'] = '%s%s' % (full_url_prefix, bundle.obj.get_absolute_url())
        
        return bundle

         
class DonorContributionResource(ModelResource):
    class Meta:
        queryset = Donor.objects.filter(published=True)
        resource_name = 'donor-contributions'
        excludes = ['type', 'location', 'title', 'bio', 'image', 'badges', 'date_added', 'date_updated', 'published', 'image_source', 'image_credit', 'image_credit_url', 'location_city', 'location_state', 'line_of_work']

    def dehydrate(self, bundle):
        contributions = []
        for rc in bundle.obj.relatedcontribution_set.all():
            #check for explainer text
            explainers = []
            if not rc.bool_party:
                for e in rc.race_explainer:
                    if e['bool_winner']:
                        winner = True
                    else:
                        winner = False
                    explainers.append({"text":e['explainer_text'],"winner":winner,"outcome_text":e['outcome_text']})
            
            #check win/loss status (can be both)
            if rc.bool_winner or rc.bool_mixedresult or rc.bool_party:
                win = True
            else:
                win = False
                
            if rc.bool_loser or rc.bool_mixedresult or rc.bool_party:
                loss = True
            else:
                loss = False
            
            contributions.append({
                "id":rc.contribution.pk,
                "date": rc.contribution.date_fixed,
                "recipient": rc.contribution.recipient_name,
                "explainers": explainers,
                "amount": int(round(rc.contribution.amount,0)),
                "bool_ballot": rc.bool_ballot,
                "bool_candidate": rc.bool_candidate,
                "bool_committee": rc.bool_committee,
                "bool_win": win,
                "bool_loss": loss,
            })
        
        bundle.data['contributions'] = contributions
        
        return bundle

   
class BadgeResource(ModelResource):
    class Meta:

        queryset = Badge.objects.filter(active=True)
        resource_name = 'badge'
        excludes = ['active','sort_order']
        filtering = {
            'slug': ALL,
        }
                    
    def dehydrate(self, bundle):
        bundle.data['full_url'] = '%s%s' % (full_url_prefix, bundle.obj.get_absolute_url())
        
        return bundle