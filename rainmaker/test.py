
import time
from django.db.models import Sum
from apps.donors.models import Donor

a = Donor.objects.all()[0]

b = a.relatedcontribution_set.filter(
    contribution__committee_party='').extra(select={
     'week': "EXTRACT(WEEK FROM date_fixed)",
     'year': "EXTRACT(YEAR FROM date_fixed)"
}).values('year', 'week').annotate(Sum('contribution__amount')).order_by('year', 'week')

print b