import csv
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView, DetailView
from django.shortcuts import render_to_response, get_object_or_404
from apps.donors.models import Donor
from apps.contributions.models import Contribution


class CSVResponseMixin(object):
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


class DonorListView(ListView):
    context_object_name = 'donor_list'
    template_name = 'donors/donors_list.html'
    queryset = Donor.objects.all().order_by('-contribs_sum')


class DonorDetailView(DetailView):
    context_object_name = 'donor'
    template_name = 'donors/donors_detail.html'
    queryset = Donor.objects.all()


class DonorContributionList(CSVResponseMixin, ListView):
    def get_queryset(self):
        donor = get_object_or_404(Donor, slug__iexact=self.kwargs['slug'])
        return Contribution.objects.filter(relatedcontribution__donor=donor).order_by('-amount')


class TimelineJSON: 
    """
    View to produce JSON for donor detail page timeline view.
    """
    pass # Code TK