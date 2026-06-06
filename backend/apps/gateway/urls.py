from django.urls import path

from . import views

urlpatterns = [
    path("v1/chat/completions/", views.GatewayChatView.as_view(), name="gateway-chat"),
    path("v1/chat/completions", views.GatewayChatView.as_view(), name="gateway-chat-no-slash"),
    path("v1/embeddings/", views.GatewayEmbeddingView.as_view(), name="gateway-embeddings"),
    path("v1/embeddings", views.GatewayEmbeddingView.as_view(), name="gateway-embeddings-no-slash"),
    path("v1/models/", views.GatewayModelsView.as_view(), name="gateway-models"),
    path("v1/models", views.GatewayModelsView.as_view(), name="gateway-models-no-slash"),
]
