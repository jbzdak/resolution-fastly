from collections import OrderedDict
import io
import typing


from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models.signals import post_save, pre_save
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
    resolution_title = models.TextField(blank=True)
    resolution_text = models.TextField(null=True)
    resolution_passed = models.NullBooleanField(default=None, null=True, blank=True)
    date_voting_finished = models.DateField(null=True, editable=False)
    public = models.BooleanField(default=True)
    render_resolution = models.BooleanField(default=False)

    def save_format(self, mimetype: str, contents: io.BytesIO):
        ResolutionFormat.objects.create(
            resolution=self,
            mimetype=mimetype,
            file=File(contents)
        )

    def __str__(self):
        return str(self.resolution_id)

    @property
    def voting_results(self) -> typing.Mapping[str, int]:
        vote_type_label_map = dict(const.VOTE_TYPES)
        defaults = {
            vote_type: 0
            for vote_type in vote_type_label_map.keys()
        }
        votes_cast = self.votes.aggregate("vote_type").annotate(
            votes=models.Count("*")
        )
        defaults.update(votes_cast)
        return OrderedDict(
            (vote_type_label_map[type_id], vote_count)
            for (type_id, vote_count) in sorted(defaults.items())
        )


class ResolutionFormat(models.Model):

    resolution = models.ForeignKey(
        Resolution,
        null=False,
        related_name="formats",
        on_delete=models.CASCADE

    )

    mimetype = models.CharField(
        max_length=256,
        null=False
    )
    file = models.FileField()

    class Models:
        ordering = (
            'mimetype',
        )


@receiver(pre_save, sender=Resolution)
def set_temporary_id(instance, **kwargs):
    if instance.resolution_id is not None:
        return
    with services.ResolutionService.inplace(instance) as service:
        service.assign_initial_signature()


@receiver(post_save, sender=Resolution)
def delete_formats(instance, **kwargs):
    if instance.pk is not None:
        instance.formats.all().delete()
    if instance.render_resolution:
        with services.ResolutionService.on(instance) as service:
            service.render_document()


class ResolutionVote(models.Model):

    vote_time = models.DateTimeField(auto_now_add=True)
    vote_type = models.PositiveSmallIntegerField(
        choices=const.VOTE_TYPES
    )

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
        ordering = (
            ("vote_time", )
        )



