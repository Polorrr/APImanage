"""Model routing CRUD views."""
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models_routing import ModelRouting
from .serializers_routing import ModelRoutingSerializer, ModelRoutingCreateSerializer


class ModelRoutingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ModelRoutingCreateSerializer
        return ModelRoutingSerializer

    def get_queryset(self):
        return ModelRouting.objects.filter(user=self.request.user).select_related("provider")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)
        return Response({"code": 0, "message": "创建成功", "data": ModelRoutingSerializer(instance).data}, status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 0, "message": "success", "data": serializer.data})


class ModelRoutingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ModelRoutingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ModelRouting.objects.filter(user=self.request.user)
