from django.views.generic import ListView, TemplateView, DetailView
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Sum
from apps.core.mixins import CSVListViewResponseMixin
from apps.donors.models import Donor, Badge
from apps.contributions.models import Contribution


########## BASE VIEWS (INHERIT FROM THESE) ##########

class DonorBaseListView(TemplateView):
    """
    Main view showing the list of top donors. Used as an index page.
    """
    context_object_name = 'donor_list'
    template_name = 'donors/donors_list.html'


class DonorBaseDetailView(DetailView):
    """
    Detail view for a given donor.
    """
    context_object_name = 'donor'
    template_name = 'donors/donors_detail.html'
    queryset = Donor.published_objects.all()


class DonorBaseContributionList(CSVListViewResponseMixin, ListView):
    """
    List of contributions for a given donor. In this case, uses the CSVListViewResponseMixin
    class to output results as CSV.
    """
    def get_queryset(self):
        donor = get_object_or_404(Donor, slug__iexact=self.kwargs['slug'])
        return Contribution.objects.filter(relatedcontribution__donor=donor).order_by('-amount')
    
    def get_context_data(self, **kwargs):
        context = super(DonorBaseContributionList, self).get_context_data(**kwargs)
        context['donor-slug'] = self.kwargs['slug']
        return context


class DonorBaseTimelineJSON(TemplateView):
    """
    View to produce JSON for the donor timeline views.
    """
    template_name = 'json/donor_chart.json'

    def get_context_data(self, **kwargs):
        donor = Donor.objects.get(slug__iexact=self.kwargs['slug'])
        contribs = donor.relatedcontribution_set.filter(contribution__date_fixed__isnull=False)
        if self.request.GET:
            if self.request.GET.has_key('type'):
                contribs = contribs.filter(contribution__recipient_party=self.request.GET['type'])
        weeks = contribs.extra(select={
                'week': "EXTRACT(WEEK FROM date_fixed)",
                'year': "EXTRACT(YEAR FROM date_fixed)"
            }).values('year', 'week').annotate(Sum('contribution__amount')).order_by('year', 'week')
        return {'weeks': weeks}

    def render_to_response(self, context, **kwargs):
        return super(DonorBaseTimelineJSON, self).render_to_response(context,
                        content_type='application/json', **kwargs)


class BadgeBaseListView(ListView):
    """
    List of badges.
    """
    context_object_name = 'badge_list'
    template_name = 'badges/badges_list.html'
    queryset = Badge.objects.filter(active=True).order_by('sort_order')
    

class BadgeBaseDetailView(DetailView):
    """
    Individual badge detail view.
    """
    context_object_name = 'badge'
    template_name = 'badges/badges_detail.html'
    queryset = Badge.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BadgeBaseDetailView, self).get_context_data(**kwargs)
        relateddonors = Badge.objects.get(slug=self.kwargs['slug']).donor_set.all()
        context['donor_list'] = relateddonors
        return context


########## CHILD VIEWS (BUILD YOUR VIEWS HERE) ##########

class DonorListView(DonorBaseListView):
    """
    Notice that this is the one overridden base view we're using. That's because
    this is the spot where it's easiest to define how the donors will be split up.
    Top 100 total? Top 50 individual and top 50 group? That logic happens here.

    Would be nice to add to the admin interface somehow, but that's for another time.
    """
    queryset = Donor.objects.filter(type='I').order_by('-contribs_sum')
    
    def get_context_data(self, **kwargs):
        context = super(DonorBaseListView, self).get_context_data(**kwargs)
        context['group_donor_list'] = Donor.groups.prefetch_related('badges').all()[:50]
        context['indiv_donor_list'] = Donor.individuals.prefetch_related('badges').all()[:50]
        context['tab'] = 'indiv'
        if self.kwargs.has_key('tab'):
            context['tab'] = self.kwargs['tab']
        return context


class DonorDetailView(DonorBaseDetailView):
    pass


class DonorContributionList(DonorBaseContributionList):
    pass


class DonorTimelineJSON(DonorBaseTimelineJSON):
    pass


class BadgeListView(BadgeBaseListView):
    pass

class BadgeDetailView(BadgeBaseDetailView):
    pass