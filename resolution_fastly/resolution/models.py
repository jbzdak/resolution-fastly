from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import const, services


class Resolution(models.Model):

    unit = models.ForeignKey(
        "unit.OrganisationalUnit", related_name="resolutions", null=False, blank=False
    )
    resolution_id = models.CharField(
        max_length=256,
        unique=True,
        blank=True,
        null=False,
        editable=False,
        default=None
    )
    resolution_text = models.TextField(null=True)
    resolution_passed = models.NullBooleanField(default=None, null=True, blank=True)
    date_voting_finished = models.DateField(null=True, editable=False)

    def __str__(self):
        return str(self.resolution_id)


@receiver(post_save, sender=Resolution)
def set_temporary_id(instance, **kwargs):
    if instance.resolution_id is not None:
        return
    with services.ResolutionService.on(instance) as service:
        service.assign_initial_signature()


class ResolutionVote(models.Model):

    vote_time = models.DateTimeField(auto_now_add=True)
    vote_type = models.PositiveSmallIntegerField(choices=const.VOTE_TYPES)

    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    resolution = models.ForeignKey(
        Resolution,
        null=False,
        related_name="votes",
    )

    class Meta:
        unique_together = (
            ("voter", "resolution")
        )



