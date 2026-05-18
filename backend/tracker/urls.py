from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, IssueViewSet, CommentViewSet, RegisterView, CustomTokenObtainPairView, AuditLogViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"issues", IssueViewSet, basename="issue")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"register", RegisterView, basename="register")
router.register(r"audit", AuditLogViewSet, basename="auditlog")

urlpatterns = [
    path("", include(router.urls)),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
