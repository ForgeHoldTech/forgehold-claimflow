from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BotLogView, ClaimViewSet, LetterSearchView

router = DefaultRouter()
router.register("claims", ClaimViewSet, basename="claim")

urlpatterns = [
    path("", include(router.urls)),
    path("bot-logs/", BotLogView.as_view(), name="bot-logs"),
    path("letters/search/", LetterSearchView.as_view(), name="letter-search"),
]