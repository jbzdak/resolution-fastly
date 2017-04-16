from django.contrib import admin

from . import models


class OwnerInline(admin.TabularInline):
    model = models.OrganisationalUnit.owners.through


class VoterInline(admin.TabularInline):
    model = models.OrganisationalUnit.voters.through


@admin.register(models.OrganisationalUnit)
class OrgAdmin(admin.ModelAdmin):

    fields = [
        'name', 'short_name', 'votes_required_to_pass'
    ]

    list_display = [
        'name', 'short_name', 'votes_required_to_pass'
    ]

    inlines = [
        OwnerInline,
        VoterInline
    ]
