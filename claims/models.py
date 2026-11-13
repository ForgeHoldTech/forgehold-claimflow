from django.db import models
from pgvector.django import VectorField


class Claim(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        IN_REVIEW = "in_review", "In Review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"

    claim_number = models.CharField(max_length=32, unique=True)
    patient_name = models.CharField(max_length=120)
    insurer = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.claim_number} - {self.patient_name}"


class DenialLetter(models.Model):
    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name="denial_letters",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    embedding = VectorField(dimensions=384, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        from .embeddings import embed_text

        self.embedding = embed_text(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.claim.claim_number} - {self.title}"