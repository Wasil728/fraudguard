from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class CheckTransactionTests(APITestCase):
    def setUp(self):
        # Runs before every test: create a test user and log in as that user
        user = User.objects.create_user("tester", password="pass12345")
        self.client.force_authenticate(user)

        # A normal transaction we can reuse
        self.normal = {
            "sender_id": "C1",
            "receiver_id": "C2",
            "txn_type": "TRANSFER",
            "amount": 5000,
            "old_balance_org": 80000,
            "new_balance_org": 75000,
            "old_balance_dest": 20000,
            "new_balance_dest": 25000,
        }

    def test_login_is_required(self):
        self.client.force_authenticate(None)  # log out
        response = self.client.post("/api/transactions/", self.normal, format="json")
        self.assertIn(response.status_code, (401, 403))

    def test_negative_balance_is_rejected(self):
        bad = dict(self.normal)
        bad["new_balance_org"] = -1
        response = self.client.post("/api/transactions/", bad, format="json")
        self.assertEqual(response.status_code, 400)

    def test_score_and_reasons_are_returned(self):
        response = self.client.post("/api/transactions/", self.normal, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(0 <= response.data["risk_score"] <= 100)
        self.assertEqual(len(response.data["explanation"]), 5)
