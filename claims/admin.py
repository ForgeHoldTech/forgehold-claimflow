from django.contrib import admin

from .models import Claim


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("claim_number", "patient_name", "insurer", "amount", "status", "created_at")
    list_filter = ("status", "insurer")
    search_fields = ("claim_number", "patient_name")