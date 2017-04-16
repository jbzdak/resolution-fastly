from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class OrganisationalUnit(models.Model):

    name = models.CharField(max_length=512, blank=False, null=False)
    short_name = models.CharField(max_length=5, blank=False, null=False)

    owners = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="+")
    voters = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="+")

    votes_required_to_pass = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name







