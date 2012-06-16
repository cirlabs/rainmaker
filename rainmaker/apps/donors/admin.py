from django.contrib import admin
from apps.donors.models import Donor, RelatedDonor, Badge

class RelatedDonorInline(admin.TabularInline):
    model = RelatedDonor
    fk_name = 'donor'
    raw_id_fields = ('related_donor',)


class DonorAdmin(admin.ModelAdmin):
    inlines = [RelatedDonorInline,]
    filter_horizontal = ('badges',)
    search_fields = ['name',]
admin.site.register(Donor, DonorAdmin)


class BadgeAdmin(admin.ModelAdmin):
    pass
admin.site.register(Badge, BadgeAdmin)
