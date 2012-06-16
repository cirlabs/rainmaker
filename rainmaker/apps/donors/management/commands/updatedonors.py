from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Count
from django.template.defaultfilters import slugify
from apps.contributions.models import Contribution, RelatedContribution
from apps.donors.models import Donor

class Command(BaseCommand):
    help = 'Aggregates contributions by donor'

    def handle(self, *args, **options):
        groups = Contribution.objects.all().values(
            "donor_name", "contributor_type").annotate(
                Sum("amount"), Count('amount')).order_by('-amount__sum')

        for g in groups:
            slug = slugify(g['donor_name'])[:45]
            if g['contributor_type']:
                slug += '-%s' % g['contributor_type'].lower()
            donor, created = Donor.objects.get_or_create(slug=slug, type=g['contributor_type'])
            
            donor.name = g['donor_name']
            donor.contribs_sum = float(g['amount__sum'])
            donor.contribs_count = float(g['amount__count'])
            donor.save()

            for contribution in Contribution.objects.filter(donor_name=donor.name):
                rc, created = RelatedContribution.objects.get_or_create(contribution=contribution, donor=donor)

        for d in Donor.objects.all():
            if len(Contribution.objects.filter(donor_name=d.name)) == 0:
                d.delete()