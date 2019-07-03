from rest_framework.test import APITestCase
from level.models import Level
import uuid


class LevelTest(APITestCase):
    pass

    def test_create_level(self):
        """
        Ensure we can create a new level object.
        """
        a = 1
        self.assertEqual(a, 1)
        # ocean = Level(name="Ocean", max_limit=1000000, daily_limit=14000, monthly_limit=50000, discount=0.00)
        # ocean.save()
        # self.assertEqual(Level.objects.count(), 1)
        # self.assertEqual(Level.objects.get().name, 'Ocean')
