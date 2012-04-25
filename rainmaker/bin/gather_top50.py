import random
from django.db.models import Sum, Count
from django.template.defaultfilters import slugify
from apps.contributions.models import Contribution, RelatedContribution
from apps.donors.models import Donor


def gather_donors(n):
	groups = Contribution.objects.filter(
		contributor_type='C').values("organization_name", ).annotate(
			Sum("amount"), Count('amount')).order_by('-amount__sum')[:n]
	for g in groups:
		donor, created = Donor.objects.get_or_create(name = g['organization_name'],
            slug = '%s-%s' % (slugify(g['organization_name'])[:45], random.randrange(1000)),
			type = 'C',
			contribs_sum = g['amount__sum'],
		    contribs_count = g['amount__count'])
		for contribution in Contribution.objects.filter(organization_name=donor.name):
			rc = RelatedContribution.objects.create(contribution=contribution, donor=donor)
	return

def gather_individs(n):
	individs = Contribution.objects.filter(
		contributor_type='I').values("contributor_name", ).annotate(
			Sum("amount"), Count('amount')).order_by('-amount__sum')[:n]
	for i in individs:
		donor, created = Donor.objects.get_or_create(name = i['contributor_name'],
            slug = '%s-%s' % (slugify(i['contributor_name'])[:45], random.randrange(1000)),
			type = 'I',
			contribs_sum = i['amount__sum'],
		    contribs_count = i['amount__count'])
		for contribution in Contribution.objects.filter(contributor_name=donor.name):
			rc = RelatedContribution.objects.create(contribution=contribution, donor=donor)
	return

if __name__ == '__main__':
	gather_groups(50)
	gather_individs(50)