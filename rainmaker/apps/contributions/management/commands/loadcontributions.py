import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from apps.contributions.models import Contribution

class Command(BaseCommand):
    help = 'Processes dates, names and other information for contributions table'
    args = args = 'path/to/file.csv'

    def handle(self, *args, **options):
        try:
            input_file = args[0]
        except IndexError:
            self.stdout.write('Please supply a path to your input file.\n')
             
        self.stdout.write('Loading contribution records (this might take a while) ...\n')
        raw_data = csv.DictReader(open(input_file, 'rU'), delimiter=',', quotechar='"')

        for row in raw_data:
            transaction_id = row['transaction_id']
            record, created = Contribution.objects.get_or_create(transaction_id=transaction_id)
            # Programmatically set model fields according to input fields. Note that
            # the model field name and the input field name from the CSV have to be
            # the same or this will crash. Shouldn't be a problem if you're using data
            # directly from NIMSP via Sunlight TransparencyData.
            # TODO: Add sane exception handling here
            for field in row.keys():
                # Get the field from the model so we can retrieve its attributes (such as null)
                modelfield = Contribution._meta.get_field(field)
                data_element = row[field]

                # Deals with special cases where blank values being fed into null fields makes
                # Postgres throw a fit.
                if modelfield.null == True:
                    if data_element == '':
                        data_element = None

                # Set the value of each field for record accordingly.
                record.__dict__[field] = data_element

            # Set specialized and custom field values, but only when the record is created for the
            # first time (to prevent overwriting of any custom cleaning done in the system)
            if created:
                if record.date:
                    record.date_fixed = datetime.strptime(record.date, '%Y-%m-%d')
                record.donor_name = record.contributor_name
                record.new_contest_result = record.seat_result
                record.related_proposition = None

            # Save
            record.save()

        self.stdout.write('Thanks for your patience! Records imported successfully!\n')