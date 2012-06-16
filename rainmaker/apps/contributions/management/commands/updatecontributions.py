from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from apps.contributions.models import Contribution

class Command(BaseCommand):
    help = 'Processes dates, names and other information for contributions table'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning contribution records ...\n')
        for contribution in Contribution.objects.all():
            old_date = contribution.date
            if old_date:
                new_date = datetime.strptime(old_date, '%Y-%m-%d')
            contribution.date_fixed = new_date

            # Standardize donor names. Eventually we'll need some more logic in here to
            # account for related donors (or will we?)
            donor_name = contribution.contributor_name
            contribution.donor_name = donor_name

            # Mark is_ballot. Will also need more logic here
            contribution.is_ballot = False

            # Standardize win/loss as new_contest_result. Will also need more logic here
            contest_result = contribution.seat_result
            contribution.new_contest_result = contest_result

            contribution.save() # Make this more efficient?
        self.stdout.write('Records cleaned!\n')
