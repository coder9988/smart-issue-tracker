from collections import Counter
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import User, Issue, Comment, AuditLog
from .serializers import UserSerializer, RegisterSerializer, IssueSerializer, CommentSerializer, AuditLogSerializer
from .permissions import IssuePermission, CommentPermission, AuditAccessPermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = User.ROLE_ADMIN if user.is_admin() else user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["role"]
    search_fields = ["username", "email"]
    ordering_fields = ["username", "role"]
    ordering = ["username"]


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.select_related("reporter", "assignee").all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IssuePermission]
    filterset_fields = ["status", "category", "priority", "reporter__id", "assignee__id"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Issue.objects.select_related("reporter", "assignee").prefetch_related("comments__author").all()
        user = self.request.user
        if user.is_admin():
            return qs
        if user.is_developer():
            return qs.filter(assignee=user)
        return qs.filter(reporter=user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def perform_destroy(self, instance):
        instance._changed_by = self.request.user
        instance.delete()

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def dashboard(self, request):
        visible = self.get_queryset()
        total = visible.count()
        open_count = visible.filter(status=Issue.STATUS_OPEN).count()
        assigned_count = visible.filter(status=Issue.STATUS_ASSIGNED).count()
        progress_count = visible.filter(status=Issue.STATUS_IN_PROGRESS).count()
        resolved_count = visible.filter(status=Issue.STATUS_RESOLVED).count()
        closed_count = visible.filter(status=Issue.STATUS_CLOSED).count()
        reopened_count = visible.filter(status=Issue.STATUS_REOPENED).count()
        critical_count = visible.filter(priority=Issue.PRIORITY_HIGH).count()
        by_category = visible.values("category").annotate(count=Count("id")).order_by("category")
        by_priority = visible.values("priority").annotate(count=Count("id")).order_by("priority")
        by_status = visible.values("status").annotate(count=Count("id")).order_by("status")
        developer_workload = (
            Issue.objects.filter(assignee__isnull=False)
            .values("assignee__username")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        recent_issues = visible.order_by("-updated_at")[:6]
        recent_comments = (
            Comment.objects.select_related("author", "issue")
            .filter(issue__in=visible)
            .order_by("-created_at")[:6]
        )
        completed = visible.filter(status__in=[Issue.STATUS_RESOLVED, Issue.STATUS_CLOSED])
        durations = [(issue.updated_at - issue.created_at).total_seconds() / 3600 for issue in completed]
        avg_resolution_hours = round(sum(durations) / len(durations), 1) if durations else 0
        return Response({
            "total": total,
            "open": open_count,
            "assigned": assigned_count,
            "in_progress": progress_count,
            "resolved": resolved_count,
            "closed": closed_count,
            "reopened": reopened_count,
            "critical": critical_count,
            "by_category": by_category,
            "by_priority": by_priority,
            "by_status": by_status,
            "developer_workload": [
                {"label": item["assignee__username"], "count": item["count"]}
                for item in developer_workload
            ],
            "avg_resolution_hours": avg_resolution_hours,
            "recent_issues": IssueSerializer(recent_issues, many=True).data,
            "recent_comments": CommentSerializer(recent_comments, many=True).data,
        })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def root_cause(self, request):
        issues = self.get_queryset()
        if not issues.exists():
            return Response({"root_causes": [], "notes": ["No issues available for analysis."]})

        descriptions = [f"{issue.title}. {issue.description}" for issue in issues]
        pairs = []
        if len(descriptions) > 1:
            vectorizer = TfidfVectorizer(stop_words="english")
            matrix = vectorizer.fit_transform(descriptions)
            similarity = cosine_similarity(matrix)
            issue_list = list(issues)
            for idx, row in enumerate(similarity):
                most_similar = row.argsort()[::-1][1:3]
                for match in most_similar:
                    score = float(row[match])
                    if score > 0.2:
                        pairs.append({
                            "issue_id": issue_list[idx].id,
                            "similar_issue_id": issue_list[match].id,
                            "score": round(score, 3),
                        })
        most_common = Counter(issue.category for issue in issues).most_common(3)
        priority_counts = Counter(issue.priority for issue in issues).most_common()
        status_counts = Counter(issue.status for issue in issues).most_common()
        assignee_counts = Counter(issue.assignee.username for issue in issues if issue.assignee).most_common(5)
        completed = [issue for issue in issues if issue.status in {Issue.STATUS_RESOLVED, Issue.STATUS_CLOSED}]
        durations = [(issue.updated_at - issue.created_at).total_seconds() / 3600 for issue in completed]
        rules = []
        if issues.count() >= 5:
            rules.append("Backlog volume is elevated; prioritize triage and ownership clarity.")
        if most_common:
            rules.append(f"Most recurring category: {most_common[0][0]}.")
        if assignee_counts:
            rules.append(f"Largest developer workload: {assignee_counts[0][0]}.")
        return Response({
            "root_causes": pairs,
            "category_counts": most_common,
            "priority_counts": priority_counts,
            "status_counts": status_counts,
            "developer_distribution": assignee_counts,
            "reopened_count": issues.filter(status=Issue.STATUS_REOPENED).count(),
            "avg_resolution_hours": round(sum(durations) / len(durations), 1) if durations else 0,
            "notes": rules,
        })


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("author", "issue").all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, CommentPermission]
    filterset_fields = ["issue__id"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, AuditAccessPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["model_name", "action", "object_id", "changed_by__id"]
    search_fields = ["model_name", "changes"]
    ordering_fields = ["timestamp", "model_name", "action"]
    ordering = ["-timestamp"]

    class AuditLogPagination(PageNumberPagination):
        page_size = 25
        page_size_query_param = "page_size"
        max_page_size = 200

    pagination_class = AuditLogPagination

    def get_queryset(self):
        qs = AuditLog.objects.select_related("changed_by").all().order_by("-timestamp")
        request = self.request
        user = request.user

        # Role-based filtering
        if not user.is_admin():
            if user.is_developer():
                # developers see only logs for issues assigned to them
                assigned_issue_ids = Issue.objects.filter(assignee=user).values_list("id", flat=True)
                qs = qs.filter(model_name__iexact="Issue", object_id__in=[str(i) for i in assigned_issue_ids])
            else:
                # reporters or others have no access
                return AuditLog.objects.none()

        # Query params filtering
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        action = request.query_params.get("action")
        user_id = request.query_params.get("user")
        issue_id = request.query_params.get("issue_id") or request.query_params.get("issue") or request.query_params.get("object_id")

        from django.utils.dateparse import parse_datetime, parse_date
        from django.utils import timezone

        if start_date:
            sd = parse_date(start_date) or parse_datetime(start_date)
            if sd:
                # make timezone-aware start of day
                if isinstance(sd, timezone.datetime) and sd.tzinfo is None:
                    sd = timezone.make_aware(sd)
                qs = qs.filter(timestamp__gte=sd)
        if end_date:
            ed = parse_date(end_date) or parse_datetime(end_date)
            if ed:
                if isinstance(ed, timezone.datetime) and ed.tzinfo is None:
                    ed = timezone.make_aware(ed)
                # include the whole day if date-only
                if not hasattr(ed, "hour"):
                    ed = timezone.make_aware(timezone.datetime(ed.year, ed.month, ed.day, 23, 59, 59))
                qs = qs.filter(timestamp__lte=ed)
        if action:
            qs = qs.filter(action__iexact=action)
        if user_id:
            qs = qs.filter(changed_by__id=user_id)
        if issue_id:
            qs = qs.filter(object_id=str(issue_id))

        return qs
