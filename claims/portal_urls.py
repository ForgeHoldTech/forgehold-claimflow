from django.urls import path

from .portal_views import portal_lookup

urlpatterns = [
    path("", portal_lookup, name="portal-lookup"),
]