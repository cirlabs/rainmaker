from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from apps.contributions.models import Contribution

class ContributionDetailView(DetailView):
    context_object_name = 'contribution'
    template_name = 'contributions/contributions_detail.html'
    queryset = Contribution.objects.all()