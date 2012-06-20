from apps.donors.models import Donor
a = Donor.objects.get(slug='gates-bill-h-i')
a.wins_money
