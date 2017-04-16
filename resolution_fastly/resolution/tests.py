import datetime

from django.test import TestCase

from resolution_fastly.users.tests.factories import UserFactory

from resolution_fastly.unit import models as unit_models

from . import models, services, const


class TestModels(TestCase):

    def setUp(self):
        self.owner = UserFactory()
        self.voters = [UserFactory(), UserFactory()]
        self.other = UserFactory()
        self.unit = unit_models.OrganisationalUnit.objects.create(
            name="Mazowsze Zachodnie",
            short_name="MAZ",
            votes_required_to_pass=1
        )
        self.unit.owners.add(self.owner)
        self.unit.voters.add(*self.voters)

    def test_id_assigned_on_creation(self):
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar"
        )
        resolution.refresh_from_db()
        self.assertTrue(
            resolution.resolution_id.startswith('PROPOSED-U-MAZ-2')
        )

    def test_assign_final_signature(self):
        today = datetime.date.today()
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar",
            resolution_passed=True
        )

        with services.ResolutionService.on(resolution) as srv:
            srv.assign_final_signature()

        resolution.refresh_from_db()
        self.assertEqual(
            resolution.resolution_id,
            "U-MAZ-{}-1".format(today.isoformat())
        )

    def test_all_have_voted(self):
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar"
        )
        with services.ResolutionService.on(resolution) as srv:
            srv.register_vote(self.voters[0], const.VOTE_TYPE_ABSTAIN)
            self.assertFalse(srv.all_have_voted())

    def test_all_have_voted_positive(self):
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar"
        )

        with services.ResolutionService.on(resolution) as srv:
            srv.register_vote(self.voters[0], const.VOTE_TYPE_ABSTAIN)
            srv.register_vote(self.voters[1], const.VOTE_TYPE_YEA)
            self.assertTrue(srv.all_have_voted())

        resolution.refresh_from_db()
        self.assertTrue(resolution.resolution_passed)

    def test_all_have_voted_negative(self):
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar"
        )

        with services.ResolutionService.on(resolution) as srv:
            srv.register_vote(self.voters[0], const.VOTE_TYPE_ABSTAIN)
            srv.register_vote(self.voters[1], const.VOTE_TYPE_NAY)
            self.assertTrue(srv.all_have_voted())

        resolution.refresh_from_db()
        self.assertFalse(resolution.resolution_passed)

    def test_already_voted(self):
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar"
        )

        with services.ResolutionService.on(resolution) as srv:
            srv.register_vote(self.voters[0], const.VOTE_TYPE_ABSTAIN)
            with self.assertRaises(services.AlreadyVoted):
                srv.register_vote(self.voters[0], const.VOTE_TYPE_ABSTAIN)

    def test_not_a_voter(self):
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar"
        )

        not_a_voter = UserFactory()

        with services.ResolutionService.on(resolution) as srv:
            with self.assertRaises(services.NotAVoter):
                srv.register_vote(not_a_voter, const.VOTE_TYPE_ABSTAIN)

    def test_voting_finished(self):
        resolution = models.Resolution.objects.create(
            unit=self.unit,
            resolution_text="Foo bar",
            resolution_passed=False,
            date_voting_finished=datetime.datetime.today()
        )
        with services.ResolutionService.on(resolution) as srv:
            with self.assertRaises(services.VotingFinished):
                srv.register_vote(self.voters[0], const.VOTE_TYPE_ABSTAIN)

