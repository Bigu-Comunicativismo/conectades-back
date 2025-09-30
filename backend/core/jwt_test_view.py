from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

class JWTTestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Endpoint protegido por JWT. Use o token Bearer para autenticação.",
        responses={200: str},
        auth=[{"JWT": []}],
    )
    def get(self, request):
        return Response({"detail": "Autenticação JWT funcionando!"})
