from django.core.management.base import BaseCommand
from pgvector.django import CosineDistance

from claims.embeddings import embed_text
from claims.models import DenialLetter


class Command(BaseCommand):
    help = "Search denial letters by meaning"

    def add_arguments(self, parser):
        parser.add_argument("query", type=str)

    def handle(self, *args, **options):
        vector = embed_text(options["query"])
        results = (
            DenialLetter.objects.exclude(embedding__isnull=True)
            .annotate(distance=CosineDistance("embedding", vector))
            .order_by("distance")[:3]
        )
        for letter in results:
            self.stdout.write(f"{letter.distance:.3f} | {letter.claim.claim_number} | {letter.title}")