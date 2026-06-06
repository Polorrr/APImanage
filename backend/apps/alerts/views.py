from rest_framework import generics, status
from rest_framework.response import Response

from .models import AlertLog, BudgetRule
from .serializers import AlertLogSerializer, BudgetRuleCreateSerializer, BudgetRuleSerializer


def success_response(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})


class BudgetRuleListView(generics.ListAPIView):
    serializer_class = BudgetRuleSerializer

    def get_queryset(self):
        return BudgetRule.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return success_response(data=self.get_serializer(qs, many=True).data)


class BudgetRuleCreateView(generics.CreateAPIView):
    serializer_class = BudgetRuleCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rule = serializer.save(user=request.user)
        return success_response(data=BudgetRuleSerializer(rule).data, message="告警规则创建成功")


class BudgetRuleListCreateView(generics.ListCreateAPIView):
    """Combined view for GET (list) and POST (create) on /alerts/rules/."""
    serializer_class = BudgetRuleCreateSerializer

    def get_queryset(self):
        return BudgetRule.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BudgetRuleCreateSerializer
        return BudgetRuleSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return success_response(data=BudgetRuleSerializer(qs, many=True).data)

    def create(self, request, *args, **kwargs):
        serializer = BudgetRuleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rule = serializer.save(user=request.user)
        return success_response(data=BudgetRuleSerializer(rule).data, message="告警规则创建成功")


class BudgetRuleUpdateView(generics.UpdateAPIView):
    serializer_class = BudgetRuleCreateSerializer

    def get_queryset(self):
        return BudgetRule.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=BudgetRuleSerializer(instance).data, message="更新成功")


class BudgetRuleDeleteView(generics.DestroyAPIView):
    def get_queryset(self):
        return BudgetRule.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="已删除")


class BudgetRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Combined view for PUT/PATCH (update) and DELETE on /alerts/rules/<pk>/."""
    serializer_class = BudgetRuleCreateSerializer

    def get_queryset(self):
        return BudgetRule.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=BudgetRuleSerializer(instance).data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="已删除")


class AlertLogListView(generics.ListAPIView):
    serializer_class = AlertLogSerializer

    def get_queryset(self):
        return AlertLog.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        return success_response(data=self.get_serializer(qs, many=True).data)
