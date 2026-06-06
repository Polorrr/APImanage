from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import ApiKey
from .serializers import ApiKeyCreateSerializer, ApiKeyListSerializer, ApiKeyUpdateSerializer


def success_response(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})


class ApiKeyListCreateView(generics.ListCreateAPIView):
    serializer_class = ApiKeyCreateSerializer

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApiKeyCreateSerializer
        return ApiKeyListSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = ApiKeyListSerializer(qs, many=True)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        api_key = serializer.save(user=request.user)
        return success_response(
            data={
                **ApiKeyListSerializer(api_key).data,
                "full_key": api_key._raw_key,
            },
            message="API Key 创建成功，请保存好密钥，后续无法再查看",
        )


class ApiKeyDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApiKeyUpdateSerializer

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=ApiKeyListSerializer(instance).data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="已吊销")


class ApiKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Combined view for PATCH (update) and DELETE on /keys/<pk>/."""
    serializer_class = ApiKeyUpdateSerializer

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=ApiKeyListSerializer(instance).data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="已吊销")
