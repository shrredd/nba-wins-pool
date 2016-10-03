######################################################################
# EXCEPTIONS
######################################################################


class DuplicateMemberException(Exception):
  pass


class InvalidMemberException(Exception):
  """ Raised when we attempt to remove someone who was never part of the Pool"""
  pass


class TooManyMembersException(Exception):
  """Raised when too many members are added to a Pool."""
  pass


class TooFewMembersException(Exception):
  """Raised when there are too few members to start a draft."""
  pass
