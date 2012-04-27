from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from apps.contributions.models import Contribution


########## BASE VIEWS (INHERIT FROM THESE) ##########

class ContributionBaseDetailView(DetailView):
    context_object_name = 'contribution'
    template_name = 'contributions/contributions_detail.html'
    queryset = Contribution.objects.all()


########## CHILD VIEWS (BUILD YOUR VIEWS HERE) ##########

class ContributionDetailView(ContributionBaseDetailView):
    pass