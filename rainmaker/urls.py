from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from apps.contributions.views import ContributionDetailView
from apps.donors.views import DonorListView, DonorDetailView, DonorContributionList

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', admin.site.urls),

    # Project URLs go here
    url(r'^$', DonorListView.as_view(), name="donor_list"),
    url(r'^donors/(?P<slug>.+)/download/$', DonorContributionList.as_view(), name="donor_download"),
    url(r'^donors/(?P<slug>.+)/$', DonorDetailView.as_view(), name="donor_detail"),
    url(r'^contributions/(?P<pk>\d+)/$', ContributionDetailView.as_view(), name="contribution_detail"),
)

urlpatterns += staticfiles_urlpatterns()