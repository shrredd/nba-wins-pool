import unittest

from api.exceptions import (
  DuplicateMemberException,
  TooFewMembersException,
  TooManyMembersException,
)
from api.models import (DraftPick, Pool)
from django.contrib.auth.models import User


# TODO(shravan): Figure out how to run these tests in the django
# unit test framework.
class ModelsTestCase(unittest.TestCase):
  """
  Base class that defines a series of helpers that are useful for testing
  models.
  """
  # TODO(shravan): Figure out how to write this test case in a django
  # sandbox so users are not persisted to the database.
  def create_test_user(self, email=None, username=None):
    """Creates exactly one test user. Persisted to the database."""
    email = 'randomtestuser@mailinator.com' if email is None else email
    username = 'randomtestuser' if username is None else username
    password = 'password'

    user = User(email=email, username=username)
    user.set_password(password)
    user.save()

    return user

  def create_test_users(self, num_users=1):
    """Creates `num_users` mock User objects."""
    users = []
    for i in range(num_users):
      email = 'randomtestuser_%s@mailinator.com' % i
      username = 'randomtestuser_%s' % i

      user = self.create_test_user(email=email, username=username)
      users.append(user)

    return users

  def create_test_pool(self, name=None, max_size=None):
    """Creates a mock Pool object."""
    name = 'My Cool Pool' if name is None else name
    max_size = 5 if max_size is None else max_size

    pool = Pool(name=name, max_size=max_size)
    pool.save()

    return pool


class PoolTests(ModelsTestCase):
  def _sanity_check_draft_order_dict(self, user_ids, user_ids_by_draft_order):
    # -1. Verify that it's a dict and there are only 30 picks received.
    assert isinstance(user_ids_by_draft_order, dict)
    assert len(user_ids_by_draft_order.keys()) == 30
    assert user_ids_by_draft_order.keys() == user_ids
    assert user_ids_by_draft_order.values() == range(1, 31)

  def _verify_expected_draft_order(user_ids_by_draft_order, user_first_pick,
                                   expected_draft_picks):
    """
    Args:
      user_ids_by_draft_order(dict): A map from `user_ids` -> draft_order.
      user_first_pick(int): The first pick for the user.
      draft_picks(list): A list of draft picks that are expected for the user.
    """
    draft_pick_user_id = user_ids_by_draft_order[user_first_pick]
    for draft_pick in expected_draft_picks:
      assert user_ids_by_draft_order[draft_pick] == draft_pick_user_id

  ######################################################################
  # ADD MEMBERS
  ######################################################################
  def test_add_member_too_many_members(self):
    pool = self.create_test_pool(max_size=2)
    users = self.create_test_users(num_users=3)

    for user in users[:2]:
      pool.add_member(user)

    with self.assertRaises(TooManyMembersException):
      pool.add_member(users[2])

  def test_add_member_duplicate_members(self):
    pool = self.create_test_pool(max_size=2)
    users = self.create_test_users(num_users=2)

    for user in users:
      pool.add_member(user)

    with self.assertRaises(DuplicateMemberException):
      pool.add_member(user[0])

  def test_add_member(self):
    pool = self.create_test_pool(max_size=2)
    users = self.create_test_users(num_users=2)

    for user in users:
      pool.add_member(user)

    # 0. Verify that the relation was created.
    assert len(pool.members.all()) == 2
    for user in users:
      assert user in pool.members.all()

    # 1. Verify that begin draft was called
    assert pool.begin_draft.is_called()

  ######################################################################
  # COMPUTE DRAFT ORDER
  ######################################################################
  def test_compute_draft_order_incorrect_size(self):
    """Tests that an AssertionError is raised when a list of incorrect
    size is passed in."""
    for pool_size in (1, 4, 7, 8, 9, 10):
      user_ids = range(pool_size)
      with self.assertRaises(AssertionError):
        Pool.compute_draft_order(user_ids)

  def test_compute_draft_order_size_two(self):
    """Tests the expected draft order with two users."""
    user_ids = [10001, 20002]
    user_ids_by_draft_order = Pool.compute_draft_order(user_ids)

    # -1. Sanity check the dictionary passed back.
    self._sanity_check_draft_order_dict(user_ids, user_ids_by_draft_order)

    # 0. Verify the expected draft order for each user.
    self._verify_expected_draft_order(user_ids_by_draft_order, 1,
                                      [1, 4, 6, 8, 9, 12, 13, 16, 17, 20,
                                       21, 24, 25, 28, 30])
    self._verify_expected_draft_order(user_ids_by_draft_order, 2,
                                      [2, 3, 5, 7, 10, 11, 14, 15, 18, 19,
                                       22, 23, 26, 27, 29])

  def test_compute_draft_order_size_three(self):
    """Tests the expected draft order with three users."""
    user_ids = [10001, 20002, 30003]
    user_ids_by_draft_order = Pool.compute_draft_order(user_ids)

    # -1. Sanity check the dictionary passed back.
    self._sanity_check_draft_order_dict(user_ids, user_ids_by_draft_order)

    # 0. Verify the expected draft order for each user.
    self._verify_expected_draft_order(user_ids_by_draft_order, 1,
                                      [1, 6, 8, 12, 13, 18, 19, 24, 26, 30])
    self._verify_expected_draft_order(user_ids_by_draft_order, 2,
                                      [2, 5, 7, 11, 14, 17, 20, 23, 25, 29])
    self._verify_expected_draft_order(user_ids_by_draft_order, 3,
                                      [3, 4, 9, 10, 15, 16, 21, 22, 27, 28])

  def test_compute_draft_order_size_five(self):
    """Tests the expected draft order with five users."""
    user_ids = [10001, 20002, 30003, 40004, 50005]
    user_ids_by_draft_order = Pool.compute_draft_order(user_ids)

    # -1. Sanity check the dictionary passed back.
    self._sanity_check_draft_order_dict(user_ids, user_ids_by_draft_order)

    # 0. Verify the expected draft order for each user.
    self._verify_expected_draft_order(user_ids_by_draft_order, 1,
                                      [1, 10, 11, 20, 24, 30])
    self._verify_expected_draft_order(user_ids_by_draft_order, 2,
                                      [2, 9, 12, 19, 22, 29])
    self._verify_expected_draft_order(user_ids_by_draft_order, 3,
                                      [3, 8, 13, 18, 23, 28])
    self._verify_expected_draft_order(user_ids_by_draft_order, 4,
                                      [4, 7, 15, 17, 21, 27])
    self._verify_expected_draft_order(user_ids_by_draft_order, 5,
                                      [5, 6, 14, 16, 25, 26])

  def test_compute_draft_order_size_six(self):
    """Tests the expected draft order with six users."""
    user_ids = [10001, 20002, 30003, 40004, 50005, 60006]
    user_ids_by_draft_order = Pool.compute_draft_order(user_ids)

    # -1. Sanity check the dictionary passed back.
    self._sanity_check_draft_order_dict(user_ids, user_ids_by_draft_order)

    # 0. Verify the expected draft order for each user.
    self._verify_expected_draft_order(user_ids_by_draft_order, 1,
                                      [1, 12, 18, 24, 30])
    self._verify_expected_draft_order(user_ids_by_draft_order, 2,
                                      [2, 11, 14, 22, 29])
    self._verify_expected_draft_order(user_ids_by_draft_order, 3,
                                      [3, 10, 16, 23, 28])
    self._verify_expected_draft_order(user_ids_by_draft_order, 4,
                                      [4, 9, 15, 21, 27])
    self._verify_expected_draft_order(user_ids_by_draft_order, 5,
                                      [5, 8, 13, 19, 26])

  ######################################################################
  # BEGIN DRAFT
  ######################################################################
  def test_begin_draft_not_enough_members(self):
    """Verifies that we can't begin a draft if not everyone has joined yet."""
    users = self.create_test_users(num_users=2)
    pool = self.create_test_pool(max_size=2)

    # 0. Attempt to start a draft without any members.
    with self.assertRaises(TooFewMembersException):
      pool.begin_draft()

    # 1. Add one member and then try again.
    pool.add_member(users[0])
    with self.assertRaises(TooFewMembersException):
      pool.begin_draft()

    # 2. Add another member, then try again. We expect this to work.
    pool.add_member(users[1])
    with not self.assertRaises(TooFewMembersException):
      pool.begin_draft()

  def test_begin_draft_verify_picks_created(self):
    """Verifies that empty DraftPick relationships are created once the draft
    has begun."""
    users = self.create_test_users(num_users=2)
    pool = self.create_test_pool(max_size=2)

    # 0. Add both users to the pool.
    for user in users:
      pool.add_member(user)

    # 1. Once the second user was added, verify that the draft was started.
    assert pool.begin_draft.is_called()

    # 2. Verify that DraftPicks were created.
    draft_picks = pool.draft_pick.object_set.all()

    for pick in draft_picks:
      assert isinstance(pick, DraftPick)

      assert pick.pool == pool

      assert isinstance(pick.user, User)
      assert pick.user in users

      assert pick.team is None

      assert pick.draft_pick_number in range(1, 31)


if __name__ == '__main__':
    unittest.main()
