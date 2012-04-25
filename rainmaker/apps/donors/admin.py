from django.contrib import admin
from apps.donors.models import Donor, Badge
from apps.contributions.models import RelatedContribution


class RelatedContributionInline(admin.TabularInline):
    model = RelatedContribution
    raw_id_fields = ('contribution',)


class DonorAdmin(admin.ModelAdmin):
    inlines = [RelatedContributionInline,]
    filter_horizontal = ('badges',)
admin.site.register(Donor, DonorAdmin)