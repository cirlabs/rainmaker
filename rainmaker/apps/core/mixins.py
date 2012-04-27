import csv
from django.http import HttpResponse


class CSVListViewResponseMixin(object):
    def render_to_response(self, context):
        return self.get_csv_response(context)

    def get_csv_response(self, context):
        """
        Convert the object_list that comes with a generic list view
        into a CSV object.
        """
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=download.csv' # Change this

        from django.db.models.query import QuerySet
        if context.has_key('object_list'):
            queryset = context['object_list']
            if type(queryset) == QuerySet:
                model_obj = model_obj = queryset[0]

        writer = csv.writer(response)
        headers = [field.name for field in model_obj._meta.fields]
        writer.writerow(headers)
        for obj in queryset:
            row = []
            for field in headers:
                if field in headers:
                    val = getattr(obj, field)
                    if callable(val):
                        val = val()
                    row.append(val)
            writer.writerow(row)
        return response