from rest_framework import generics, status
from rest_framework.response import Response

from apps.gateway.models import LLMCallLog
from apps.gateway.serializers import LLMCallLogSerializer
from . import services


def success_response(data=None, message="success"):
    return Response({"code": 0, "message": message, "data": data})


class StatsOverviewView(generics.GenericAPIView):
    def get(self, request):
        days = int(request.query_params.get("days", 30))
        agent_id = request.query_params.get("agent_id")
        data = services.get_overview(request.user.id, days, agent_id=agent_id)
        return success_response(data=data)


class StatsDailyView(generics.GenericAPIView):
    def get(self, request):
        days = int(request.query_params.get("days", 30))
        agent_id = request.query_params.get("agent_id")
        data = services.get_daily_trend(request.user.id, days, agent_id=agent_id)
        return success_response(data=data)


class StatsByModelView(generics.GenericAPIView):
    def get(self, request):
        days = int(request.query_params.get("days", 30))
        agent_id = request.query_params.get("agent_id")
        data = services.get_by_model(request.user.id, days, agent_id=agent_id)
        return success_response(data=data)


class StatsByAgentView(generics.GenericAPIView):
    def get(self, request):
        days = int(request.query_params.get("days", 30))
        data = services.get_by_agent(request.user.id, days)
        return success_response(data=data)


class StatsByProviderView(generics.GenericAPIView):
    def get(self, request):
        days = int(request.query_params.get("days", 30))
        data = services.get_by_provider(request.user.id, days)
        return success_response(data=data)


class CallLogsView(generics.ListAPIView):
    serializer_class = LLMCallLogSerializer

    def get_queryset(self):
        return services.get_call_logs(
            self.request.user.id,
            model=self.request.query_params.get("model"),
            agent_id=self.request.query_params.get("agent_id"),
            status_code=self.request.query_params.get("status_code"),
            start_date=self.request.query_params.get("start_date"),
            end_date=self.request.query_params.get("end_date"),
        )

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated = self.get_paginated_response(serializer.data)
            return Response({"code": 0, "message": "success", "data": paginated.data})
        serializer = self.get_serializer(qs, many=True)
        return Response({"code": 0, "message": "success", "data": serializer.data})
