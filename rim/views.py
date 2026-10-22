from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .engine import RIM_API_Endpoint


class RIMProcessView(APIView):
    """
    POST /api/rim/process/
    Body: { "input": "I want to transfer $2000", "max_limit": 5000 }
    Returns RIM System 1→2→3 analysis result.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_input = request.data.get("input", "").strip()
        max_limit = int(request.data.get("max_limit", 5000))

        if not user_input:
            return Response(
                {"error": "Field 'input' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = RIM_API_Endpoint(user_input, max_transaction_limit=max_limit)
        return Response(result, status=status.HTTP_200_OK)


class RIMHealthView(APIView):
    """
    GET /api/rim/health/
    Returns RIM engine version and status.
    """
    permission_classes = []  # Public health check

    def get(self, request):
        return Response({
            "status": "online",
            "engine": "RIM Core Engine V3",
            "architecture": ["System1_Intuition", "System2_Logic", "System3_MetaCognition"],
            "endpoint": "/api/rim/process/"
        })
