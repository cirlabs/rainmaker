from django.contrib import admin
from apps.donors.models import Donor, RelatedDonor, Badge


class RelatedDonorInline(admin.TabularInline):
    model = RelatedDonor
    fk_name = 'donor'
    raw_id_fields = ('related_donor',)


class DonorAdmin(admin.ModelAdmin):
    inlines = [RelatedDonorInline,]
    filter_horizontal = ('badges',)
    list_display = ['name', 'type', 'line_of_work', 'contribs_sum', 'contribs_count',
                     'date_added', 'date_updated', 'published']
    search_fields = ['name', 'location_city', 'location_state', 'line_of_work', 'bio']
    list_filter = ['type',]
    list_editable = ['published']
    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'bio', 'line_of_work', 'published')
        }),
        ('Location information', {
            'fields': ('location_city', 'location_state')
        }),
        ('Image information', {
            'fields': ('image', 'image_credit', 'image_credit_url')
        }),
        ('Contribution information', {
            'fields': ('contribs_count', 'contribs_sum', 'badges')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug',)
        }),
    )
admin.site.register(Donor, DonorAdmin)


class BadgeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'short_description', 'long_description', 'image')
        }),
        ('Display information', {
            'fields': ('active', 'sort_order')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug',)
        }),
    )
admin.site.register(Badge, BadgeAdmin)