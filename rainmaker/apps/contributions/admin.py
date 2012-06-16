from django.contrib import admin
from apps.contributions.models import Contribution

# TODO: Clean up fields in actual admin forms

class ContributionAdmin(admin.ModelAdmin):
    search_fields = ['contributor_name', 'organization_name', 'recipient_name',
                    'parent_organization_name', 'committee_name']
    list_display = ['contributor_name', 'contributor_city', 'contributor_state', 'contributor_zipcode',
                    'amount', 'date', 'recipient_name', 'seat', 'related_proposition']
    list_filter = ['cycle', 'recipient_type']
    list_editable = ['related_proposition']
admin.site.register(Contribution, ContributionAdmin)