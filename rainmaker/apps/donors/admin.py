from django.contrib import admin
from apps.donors.models import Donor, RelatedDonor, Badge


class RelatedDonorInline(admin.TabularInline):
    model = RelatedDonor
    fk_name = 'donor'
    raw_id_fields = ('related_donor',)


class DonorAdmin(admin.ModelAdmin):
    inlines = [RelatedDonorInline,]
    filter_horizontal = ('badges',)
    list_display = ['name', 'type', 'location', 'line_of_work', 'contribs_sum', 'contribs_count',
                     'date_added', 'date_updated', 'published']
    search_fields = ['name', 'location', 'line_of_work', 'bio', 'title']
    list_filter = ['type',]
    list_editable = ['published']
admin.site.register(Donor, DonorAdmin)


class BadgeAdmin(admin.ModelAdmin):
    pass
admin.site.register(Badge, BadgeAdmin)