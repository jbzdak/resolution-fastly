from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class Voter(models.Model):

    slack_id = models.CharField(max_length=512, null=True, blank=True)
    full_name = models.CharField(max_length=1024, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)


class OrganisationalUnit(models.Model):

    name = models.CharField(max_length=512, blank=False, null=False)
    short_name = models.CharField(max_length=5, blank=False, null=False)

    owners = models.ManyToManyField(settings.AUTH_USER_MODEL)
    voters = models.ManyToManyField(Voter)

    votes_required_to_pass = models.IntegerField(validators=[MinValueValidator(0)])







