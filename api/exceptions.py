######################################################################
# EXCEPTIONS
######################################################################


class TooManyMembersException(Exception):
  """Raised when too many members are added to a Pool."""
  pass


class TooFewMembersException(Exception):
  """Raised when there are too few members to start a draft."""
  pass


class DuplicateMemberException(Exception):
  pass
