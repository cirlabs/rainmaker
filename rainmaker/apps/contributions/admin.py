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
    fieldsets = (
        (None, {
            'fields': ('transaction_id', 'cycle', 'date_fixed', 'amount', 'donor_name', 'recipient_name')
        }),
        ('Contributor information (general)', {
            'fields': ('contributor_name', 'contributor_ext_id', 'contributor_type', 'contributor_occupation',
                'contributor_employer', 'contributor_city', 'contributor_state', 'contributor_zipcode',
                'contributor_category')
        }),
        ('Contributor information (organization)', {
            'fields': ('organization_name', 'organization_ext_id', 'parent_organization_name', 'parent_organization_ext_id')
        }),
        ('Recipient information', {
            'fields': ('recipient_ext_id', 'recipient_party', 'recipient_type', 'recipient_state', 'recipient_state_held',
                'recipient_category', 'candidacy_status', 'district', 'district_held', 'seat', 'seat_status', 'seat_result')
        }),
        ('NIMSP metadata', {
            'classes': ('collapse',),
            'fields': ('transaction_namespace', 'transaction_type', 'filing_id', 'is_amendment'),
        }),
        ('Added fields', {
            'classes': ('collapse',),
            'fields': ('related_proposition',),
        }),
    )
admin.site.register(Contribution, ContributionAdmin)