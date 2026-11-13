from datetime import datetime, timedelta, timezone

from django.core.management.base import BaseCommand

from claims.models import Claim, DenialLetter
from claims.mongo import get_db

CLAIMS = [
    ("CLM-3001", "Hamza Tariq", "Northstar Health", "42500.00", Claim.Status.APPROVED),
    ("CLM-3002", "Ayesha Siddiqui", "Crescent Assurance", "18900.00", Claim.Status.DENIED),
    ("CLM-3003", "Bilal Raza", "Bluepeak Insurance", "76000.00", Claim.Status.IN_REVIEW),
    ("CLM-3004", "Sana Malik", "Northstar Health", "9500.00", Claim.Status.SUBMITTED),
    ("CLM-3005", "Usman Farooq", "Crescent Assurance", "31200.00", Claim.Status.DENIED),
    ("CLM-3006", "Zainab Hussain", "Bluepeak Insurance", "56800.00", Claim.Status.APPROVED),
]

LETTERS = [
    (
        "CLM-3002",
        "Missing documents",
        "Your claim was denied because the discharge summary and itemized bill were not attached to the submission. Please send both documents to the claims department to have the claim reviewed again.",
    ),
    (
        "CLM-3005",
        "Pre-authorization missing",
        "The claim was denied because the procedure required prior authorization from the insurer, and no authorization number was provided with the submission.",
    ),
    (
        "CLM-3005",
        "Out-of-network provider",
        "This claim cannot be paid because the treating hospital is not part of the insurer's approved network for the patient's current plan.",
    ),
    (
        "CLM-3005",
        "Late submission",
        "The claim was submitted more than 90 days after the date of treatment, which exceeds the filing deadline defined in the policy.",
    ),
]

BOT_LOGS = [
    (
        "CLM-3001",
        "success",
        "Claim status fetched from portal",
        {"patient": "Hamza Tariq", "insurer": "Northstar Health", "amount": "42500.00", "status": "Approved"},
    ),
    (
        "CLM-3002",
        "success",
        "Claim status fetched from portal",
        {"patient": "Ayesha Siddiqui", "insurer": "Crescent Assurance", "amount": "18900.00", "status": "Denied"},
    ),
    (
        "CLM-3003",
        "success",
        "Claim status fetched from portal",
        {"patient": "Bilal Raza", "insurer": "Bluepeak Insurance", "amount": "76000.00", "status": "In Review"},
    ),
    (
        "CLM-3099",
        "not_found",
        "Claim not found on portal",
        {},
    ),
    (
        "CLM-3005",
        "error",
        "Timeout 30000ms exceeded while waiting for the portal result",
        {},
    ),
]


class Command(BaseCommand):
    help = "Create demo claims, denial letters and bot logs"

    def handle(self, *args, **options):
        for claim_number, patient, insurer, amount, claim_status in CLAIMS:
            Claim.objects.get_or_create(
                claim_number=claim_number,
                defaults={
                    "patient_name": patient,
                    "insurer": insurer,
                    "amount": amount,
                    "status": claim_status,
                },
            )

        for claim_number, title, content in LETTERS:
            claim = Claim.objects.get(claim_number=claim_number)
            DenialLetter.objects.get_or_create(
                claim=claim,
                title=title,
                defaults={"content": content},
            )

        collection = get_db().bot_logs
        if collection.count_documents({"demo": True}) == 0:
            now = datetime.now(timezone.utc)
            documents = []
            for index, (claim_number, result, message, details) in enumerate(BOT_LOGS):
                documents.append(
                    {
                        "bot_name": "portal_status_checker",
                        "claim_number": claim_number,
                        "result": result,
                        "message": message,
                        "details": details,
                        "created_at": now - timedelta(minutes=5 * (len(BOT_LOGS) - index)),
                        "demo": True,
                    }
                )
            collection.insert_many(documents)

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))