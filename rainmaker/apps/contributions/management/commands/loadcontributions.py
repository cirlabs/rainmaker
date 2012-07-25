import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from apps.contributions.models import Contribution

def create_records(records):
    '''
    Helper function to bulk create records.
    '''
    Contribution.objects.bulk_create(records)
    return


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

        i = 0 # Loop counter to trigger bulk saves
        bulk_records = []
        while True:
            # Manually iterate and be sure to save on final iteration
            try:
                row = raw_data.next()
            except StopIteration: # This is thrown once the iterator is empty, which triggers save on last item
                create_records(bulk_records)
                self.stdout.write('%s records created ...\n' % i) 
                break # Be sure to break the loop. This is is the exit condition.

            transaction_id = row['transaction_id']
            created = False
            try: # Manual step-through of get_or_create sans the commit
                record = Contribution.objects.get(transaction_id=transaction_id)
            except Contribution.DoesNotExist:
                record = Contribution()
                created = True
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

            # Bulk insert every 5,000 records
            bulk_records.append(record)
            if i % 5000 == 0:
                create_records(bulk_records)
                self.stdout.write('%s records created ...\n' % i)            
                bulk_records = []

            i += 1 # Increment

        self.stdout.write('Thanks for your patience! Records imported successfully!\n')
