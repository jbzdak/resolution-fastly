from django.contrib import admin

from . import models


class VoteAdmin(admin.TabularInline):
    model = models.ResolutionVote


@admin.register(models.Resolution)
class ResolutionAdmin(admin.ModelAdmin):

    fields = (
        'unit',
        'resolution_id',
        'resolution_text',
        'resolution_passed',
        'date_voting_finished'
    )

    readonly_fields = (
        'unit',
        'resolution_id',
        'resolution_passed',
        'date_voting_finished'
    )

    readonly_fields_new = (
        'resolution_id',
        'resolution_passed',
        'date_voting_finished'
    )

    readonly_fields_passed = fields

    inlines = [
        VoteAdmin
    ]

    def get_readonly_fields(
        self, request, obj=None
    ):
        if obj is None:
            return self.readonly_fields_new
        if obj.resolution_passed:
            return self.readonly_fields_passed
        return self.readonly_fields


