from django.contrib import admin
from apps.props.models import Proposition, RelatedCommittee

class RelatedCommitteeInline(admin.TabularInline):
    model = RelatedCommittee
    raw_id_fields = ('donor',)


class PropositionAdmin(admin.ModelAdmin):
    inlines = [RelatedCommitteeInline,]
    list_display = ['title', 'cycle', 'result', 'ext_link']
    search_fields = ['title', 'number']
    list_filter = ['cycle', 'result']
admin.site.register(Proposition, PropositionAdmin)