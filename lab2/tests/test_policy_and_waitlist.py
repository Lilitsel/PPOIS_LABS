import unittest
from tests.factories import make_client, make_tour
from travel_agency.booking.booking import Waitlist
from travel_agency.booking.policy import CancellationPolicy
from travel_agency.exceptions import CapacityExceededException


class PolicyAndWaitlistTest(unittest.TestCase):
    def test_policy(self):
        policy = CancellationPolicy()
        self.assertEqual(policy.penalty_percent_for(40), 0)
        self.assertEqual(policy.penalty_percent_for(20), 25)
        self.assertEqual(policy.penalty_percent_for(-1), 100)
        self.assertEqual(policy.calculate_penalty(1000.0, 10), 500.0)

    def test_waitlist(self):
        tour = make_tour(max_group=1)
        waitlist = Waitlist(tour, 2)
        first, second = make_client("C1"), make_client("C2")
        self.assertEqual(waitlist.enqueue(first), 1)
        self.assertEqual(waitlist.enqueue(first), 1)
        self.assertEqual(waitlist.enqueue(second), 2)
        with self.assertRaises(CapacityExceededException):
            waitlist.enqueue(make_client("C3"))
        tour.reserve_places(1)
        self.assertIsNone(waitlist.promote_next())
        tour.release_places(1)
        self.assertIs(waitlist.promote_next(), first)
        self.assertEqual(waitlist.position_of(first), 0)


if __name__ == "__main__":
    unittest.main()
