# coding=utf8
from django.utils.translation import ugettext_lazy

VOTE_TYPE_YEA = 1
VOTE_TYPE_NAY = 2
VOTE_TYPE_ABSTAIN = 3
VOTE_TYPE_INVALID = 4

VOTE_TYPES = (
    (VOTE_TYPE_YEA, ugettext_lazy("Yes")),
    (VOTE_TYPE_NAY, ugettext_lazy("No")),
    (VOTE_TYPE_ABSTAIN, ugettext_lazy("Abstain")),
    (VOTE_TYPE_INVALID, ugettext_lazy("Invalid vote"))
)
