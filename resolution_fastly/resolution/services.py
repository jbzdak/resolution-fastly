# coding=utf8

import datetime
import typing

from decorator import contextmanager
from django.conf import settings
from django.db import transaction



from . import const

from . import models
from resolution_fastly.unit import models as unit_models


class VoteException(ValueError):
    pass


class NotAVoter(VoteException):
    """
    Raised when we try to register someone as a voter, and this person is not eligible to vote. 
    """


class AlreadyVoted(VoteException):
    """
    Raised when someone already voted, and vote can't be changed. 
    """


class VotingFinished(VoteException):
    """
    Raised when someone tries to vote on a resolution that can't be voted right now. 
    """


class ResolutionService(object):

    @classmethod
    @contextmanager
    def on(cls, resolution: 'models.Resolution') -> 'ResolutionService':
        with transaction.atomic():
            try:
                unit = unit_models.OrganisationalUnit.objects.filter(
                    pk=resolution.unit.pk).select_for_update().get()
                resolution = models.Resolution.objects.filter(
                    pk=resolution.pk).select_for_update().get()
                yield ResolutionService(
                    resolution=resolution,
                    unit=unit
                )
                resolution.save()
            finally:
                pass

    def __init__(
        self,
        resolution: 'models.Resolution',
        unit: 'unit_models.OrganisationalUnit'
    ):
        self.resolution = resolution
        self.unit = unit

    def __format_signature(
        self,
        template: str,
        date: datetime.date,
        id_for_day: int
    ):
        return template.format(
            unit=self.unit,
            resolution=self.resolution,
            date=date.isoformat(),
            today=self.resolution.date_voting_finished,
            idx=id_for_day
        )

    def __get_resolution_id(self, resolution_state=True):
        todays_passed_resolutions = self.unit.resolutions.filter(
            date_voting_finished=self.resolution.date_voting_finished,
            resolution_passed=True
        ).exclude(pk=self.resolution.pk)
        return todays_passed_resolutions.count() + 1

    def assign_final_signature(self):
        # This assumes resolution has passed with yea vote
        self.resolution.date_voting_finished = datetime.date.today()
        self.resolution.resolution_id = self.__format_signature(
            template=settings.RESOLUTION_FASTLY["PASSED_RESOLUTION_SIGNATURE"],
            id_for_day=self.__get_resolution_id(),
            date=self.resolution.date_voting_finished
        )

    def all_have_voted(self) -> bool:
        total_voters = self.unit.voters.count()
        votes = self.resolution.votes.count()
        return votes >= total_voters

    def verify_voter(self, voter):
        if self.resolution.resolution_passed is not None:
            raise VotingFinished()
        if not self.resolution.unit.voters.filter(pk=voter.pk).exists():
            raise NotAVoter()
        if self.resolution.votes.filter(voter = voter).exists():
            raise AlreadyVoted()

    def register_vote(self, voter: settings.AUTH_USER_MODEL, vote: int):
        self.verify_voter(voter)
        models.ResolutionVote.objects.create(
            resolution=self.resolution,
            voter=voter,
            vote_type=vote
        )
        if self.all_have_voted():
            self.finish_voting()

    def assign_initial_signature(self):
        self.resolution.resolution_id = self.__format_signature(
            template=settings.RESOLUTION_FASTLY["PROPOSED_RESOLUTION_SIGNATURE"],
            id_for_day=self.resolution.pk,
            date=datetime.date.today()
        )

    def finish_voting(self):
        # NOTE: This assumes voting has reached minimum votes
        yes_votes = self.resolution.votes.filter(vote_type=const.VOTE_TYPE_YEA).count()
        passed = self.resolution.unit.votes_required_to_pass <= yes_votes
        self.resolution.resolution_passed = passed
        if passed:
            self.assign_final_signature()

