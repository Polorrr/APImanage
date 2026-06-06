from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response

from .models import ModelPricing
from .serializers import ModelPricingCreateSerializer, ModelPricingSerializer


def success_response(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})


class ModelPricingListCreateView(generics.ListCreateAPIView):
    serializer_class = ModelPricingCreateSerializer

    def get_queryset(self):
        return ModelPricing.objects.filter(
            models.Q(user=self.request.user) | models.Q(is_builtin=True)
        ).distinct()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ModelPricingCreateSerializer
        return ModelPricingSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = ModelPricingSerializer(qs, many=True)
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pricing = serializer.save(user=request.user)
        return success_response(data=ModelPricingSerializer(pricing).data, message="价格添加成功")


class ModelPricingDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ModelPricingCreateSerializer

    def get_queryset(self):
        return ModelPricing.objects.filter(user=self.request.user, is_builtin=False)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=ModelPricingSerializer(instance).data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="已删除")


class BuiltinPricingListView(generics.ListAPIView):
    serializer_class = ModelPricingSerializer

    def get_queryset(self):
        return ModelPricing.objects.filter(is_builtin=True)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return success_response(data=self.get_serializer(qs, many=True).data)
