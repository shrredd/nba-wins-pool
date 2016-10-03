import unittest

from .models import Pool


class PoolTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
