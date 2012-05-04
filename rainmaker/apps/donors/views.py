from django.views.generic import ListView, TemplateView, DetailView
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Sum
from apps.core.mixins import CSVListViewResponseMixin
from apps.donors.models import Donor
from apps.contributions.models import Contribution


########## BASE VIEWS (INHERIT FROM THESE) ##########

class DonorBaseListView(ListView):
    context_object_name = 'donor_list'
    template_name = 'donors/donors_list.html'
    queryset = Donor.objects.all().order_by('-contribs_sum')


class DonorBaseDetailView(DetailView):
    context_object_name = 'donor'
    template_name = 'donors/donors_detail.html'
    queryset = Donor.objects.all()


class DonorBaseContributionList(CSVListViewResponseMixin, ListView):
    def get_queryset(self):
        donor = get_object_or_404(Donor, slug__iexact=self.kwargs['slug'])
        return Contribution.objects.filter(relatedcontribution__donor=donor).order_by('-amount')


class DonorBaseTimelineJSON(TemplateView):
    template_name = 'json/donor_chart.json'

    def get_context_data(self, **kwargs):
        donor = Donor.objects.get(slug__iexact=self.kwargs['slug'])
        weeks = donor.relatedcontribution_set.filter(
            contribution__committee_party='').extra(select={
                'week': "EXTRACT(WEEK FROM date_fixed)",
                'year': "EXTRACT(YEAR FROM date_fixed)"
            }).values('year', 'week').annotate(Sum('contribution__amount')).order_by('year', 'week')
        return {'weeks': weeks}


########## CHILD VIEWS (BUILD YOUR VIEWS HERE) ##########

class DonorListView(DonorBaseListView):
    pass


class DonorDetailView(DonorBaseDetailView):
    pass


class DonorContributionList(DonorBaseContributionList):
    pass


class DonorTimelineJSON(DonorBaseTimelineJSON):
    pass