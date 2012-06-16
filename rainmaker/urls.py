from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from tastypie.api import Api
from apps.donors.api import DonorResource, BadgeResource, DonorContributionResource
from apps.contributions.views import ContributionDetailView
from apps.donors.views import *

admin.autodiscover()

# Tastypie API setup
v1_api = Api(api_name='v1')
v1_api.register(DonorResource())
v1_api.register(BadgeResource())
v1_api.register(DonorContributionResource())

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', admin.site.urls),

    # Donor list views
    url(r'^$', DonorListView.as_view(), name="donor_list"),
    url(r'^groups/$', DonorListView.as_view(), {'tab':'group'}, name="donor_list_grouptab"),
    url(r'^individuals/$', DonorListView.as_view(), {'tab':'indiv'}, name="donor_list_indivtab"),

    # Donor detail views
    url(r'^donors/(?P<slug>.+)/download/$', DonorContributionList.as_view(), name="donor_download"),
    url(r'^donors/(?P<slug>.+)/$', DonorDetailView.as_view(), name="donor_detail"),
    url(r'^json/timeline/(?P<slug>.+)/$', DonorTimelineJSON.as_view(), name="timeline_json"),

    # Badges
    url(r'^badges/(?P<slug>.+)$', BadgeDetailView.as_view(), name="badge_detail"),
    url(r'^badges/$', BadgeListView.as_view(), name="badge_list"),

    # API URLs
    (r'^api/', include(v1_api.urls)),
)

urlpatterns += staticfiles_urlpatterns()