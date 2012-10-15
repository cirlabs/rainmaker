from django.db.models import Sum, Count
from django.template.defaultfilters import slugify
from apps.contributions.models import Contribution, RelatedContribution
from apps.donors.models import Donor

groups = Contribution.objects.all().values(
    "donor_name", "contributor_type").annotate(
        Sum("amount"), Count('amount')).order_by('-amount__sum')

for donor in Donor.objects.all():
    donor._set_cand_contrib_count()
    donor._set_cmte_contrib_count()
    donor._set_ballot_contrib_count()
    donor.save()