from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Claim


class ClaimApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            password="StrongPass12345",
        )
        self.client = APIClient()
        self.claim = Claim.objects.create(
            claim_number="CLM-1001",
            patient_name="Ali Khan",
            insurer="State Life",
            amount="15000.00",
        )

    def test_claims_require_authentication(self):
        response = self.client.get("/api/claims/")
        self.assertEqual(response.status_code, 401)

    def test_token_login_returns_access_token(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "tester", "password": "StrongPass12345"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_list_claims(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/claims/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["claim_number"], "CLM-1001")

    def test_create_claim(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/api/claims/",
            {
                "claim_number": "CLM-1002",
                "patient_name": "Sara Ahmed",
                "insurer": "EFU Health",
                "amount": "8200.50",
                "status": "submitted",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Claim.objects.filter(claim_number="CLM-1002").exists())

    def test_check_status_queues_background_task(self):
        self.client.force_authenticate(user=self.user)
        with patch("claims.views.check_claim_status") as mocked_task:
            mocked_task.delay.return_value.id = "task-123"
            response = self.client.post(f"/api/claims/{self.claim.id}/check-status/")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()["task_id"], "task-123")
        mocked_task.delay.assert_called_once_with("CLM-1001")


class PortalTests(TestCase):
    def setUp(self):
        Claim.objects.create(
            claim_number="CLM-2001",
            patient_name="Bilal Raza",
            insurer="Jubilee Health",
            amount="12000.00",
            status=Claim.Status.APPROVED,
        )

    def test_portal_shows_existing_claim(self):
        response = self.client.get("/portal/", {"claim_number": "CLM-2001"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bilal Raza")
        self.assertContains(response, "Approved")

    def test_portal_handles_unknown_claim(self):
        response = self.client.get("/portal/", {"claim_number": "CLM-9999"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No claim found")