from datetime import datetime, timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Claim
from .mongo import get_db
from .serializers import ClaimSerializer
from .tasks import check_claim_status


class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer

    @action(detail=True, methods=["post"], url_path="check-status")
    def check_status(self, request, pk=None):
        claim = self.get_object()
        task = check_claim_status.delay(claim.claim_number)
        return Response(
            {"task_id": task.id, "claim_number": claim.claim_number},
            status=status.HTTP_202_ACCEPTED,
        )


class BotLogView(APIView):
    def get(self, request):
        logs = []
        cursor = get_db().bot_logs.find().sort("created_at", -1).limit(50)
        for document in cursor:
            document["id"] = str(document.pop("_id"))
            document["created_at"] = document["created_at"].isoformat()
            logs.append(document)
        return Response(logs)

    def post(self, request):
        payload = {key: value for key, value in request.data.items()}
        created_at = datetime.now(timezone.utc)
        payload["created_at"] = created_at
        result = get_db().bot_logs.insert_one(payload)
        payload.pop("_id", None)
        payload["id"] = str(result.inserted_id)
        payload["created_at"] = created_at.isoformat()
        return Response(payload, status=status.HTTP_201_CREATED)