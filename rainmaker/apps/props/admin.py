from django.contrib import admin
from apps.props.models import Proposition, RelatedCommittee

class RelatedCommitteeInline(admin.TabularInline):
    model = RelatedCommittee
    raw_id_fields = ('donor',)


class PropositionAdmin(admin.ModelAdmin):
    inlines = [RelatedCommitteeInline,]
admin.site.register(Proposition, PropositionAdmin)
