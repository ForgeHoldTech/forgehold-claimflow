from django.contrib import admin

from .models import Claim, DenialLetter


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("claim_number", "patient_name", "insurer", "amount", "status", "created_at")
    list_filter = ("status", "insurer")
    search_fields = ("claim_number", "patient_name")


@admin.register(DenialLetter)
class DenialLetterAdmin(admin.ModelAdmin):
    list_display = ("claim", "title", "created_at")
    search_fields = ("title", "content")