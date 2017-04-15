from django.db import models

from . import const


class Resolution(models.Model):

    unit = models.ForeignKey(
        "unit.OrganisationalUnit", related_name="resolutions", null=False, blank=False
    )
    resolution_id = models.CharField(max_length=256, unique=True, null=True)
    resolution_text = models.CharField(null=True)
    resolution_passed = models.NullBooleanField(default=None, null=True, blank=True)
    date_voting_finished = models.DateField(null=True, editable=False)


class ResolutionVote(models.Model):

    vote_time = models.DateTimeField(auto_now_add=True)
    vote_type = models.PositiveSmallIntegerField(choices=const.VOTE_TYPES)

    voter = models.ForeignKey("unit.Voter")
    resolution = models.ForeignKey(Resolution, null=False, related_name="votes")

    class Meta:
        unique_together = (
            ("voter", "resolution")
        )



