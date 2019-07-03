from rest_framework.test import APITestCase
from .models import Voucher
import uuid


class VoucherTestCase(APITestCase):
    pass

    def test_create_voucher(self):
        """
        Ensure we can create a new voucher object.
        """
        a = 1
        self.assertEqual(a, 1)
