from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def root_view(request):
    return JsonResponse({
        "name": "Smart Issue Tracker API",
        "status": "ok",
        "endpoints": {
            "api": "/api/",
            "admin": "/admin/",
            "swagger": "/swagger/",
            "redoc": "/redoc/",
            "health": "/health/",
        },
    })


def health_view(request):
    return JsonResponse({"status": "ok"})


schema_view = get_schema_view(
    openapi.Info(
        title="PEP Issue Tracker API",
        default_version="v1",
        description="Smart issue tracker API with JWT auth and analytics",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", root_view, name="root"),
    path("health/", health_view, name="health"),
    path("admin/", admin.site.urls),
    path("api/", include("tracker.urls")),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
