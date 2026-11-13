from django.shortcuts import render

from .models import Claim


def portal_lookup(request):
    claim_number = request.GET.get("claim_number", "").strip()
    searched = bool(claim_number)
    claim = None
    if searched:
        claim = Claim.objects.filter(claim_number__iexact=claim_number).first()
    context = {
        "claim_number": claim_number,
        "searched": searched,
        "claim": claim,
    }
    return render(request, "portal/lookup.html", context)