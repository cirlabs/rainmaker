from django.views.generic import ListView, TemplateView, DetailView
from django.shortcuts import render_to_response, get_object_or_404
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


########## CHILD VIEWS (BUILD YOUR VIEWS HERE) ##########

class DonorListView(DonorBaseListView):
    pass


class DonorDetailView(DonorBaseDetailView):
    pass


class DonorContributionList(DonorBaseContributionList):
    pass