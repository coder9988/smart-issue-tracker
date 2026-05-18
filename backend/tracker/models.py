from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_DEVELOPER = "developer"
    ROLE_REPORTER = "reporter"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_DEVELOPER, "Developer"),
        (ROLE_REPORTER, "Reporter"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_REPORTER)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def is_developer(self):
        return self.role == self.ROLE_DEVELOPER

    def is_reporter(self):
        return self.role == self.ROLE_REPORTER


class Issue(models.Model):
    STATUS_OPEN = "open"
    STATUS_ASSIGNED = "assigned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"
    STATUS_REOPENED = "reopened"

    CATEGORY_BUG = "bug"
    CATEGORY_FEATURE = "feature"
    CATEGORY_TASK = "task"
    CATEGORY_OTHER = "other"

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_CLOSED, "Closed"),
        (STATUS_REOPENED, "Reopened"),
    ]
    CATEGORY_CHOICES = [
        (CATEGORY_BUG, "Bug"),
        (CATEGORY_FEATURE, "Feature"),
        (CATEGORY_TASK, "Task"),
        (CATEGORY_OTHER, "Other"),
    ]
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    reporter = models.ForeignKey(User, related_name="reported_issues", on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name="assigned_issues", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

    def can_transition_to(self, new_status, by_user=None):
        transitions = {
            self.STATUS_OPEN: {self.STATUS_ASSIGNED},
            self.STATUS_ASSIGNED: {self.STATUS_IN_PROGRESS},
            self.STATUS_IN_PROGRESS: {self.STATUS_RESOLVED},
            self.STATUS_RESOLVED: {self.STATUS_CLOSED, self.STATUS_REOPENED},
            self.STATUS_CLOSED: {self.STATUS_REOPENED},
            self.STATUS_REOPENED: {self.STATUS_ASSIGNED, self.STATUS_IN_PROGRESS},
        }

        allowed = transitions.get(self.status, set())
        if new_status not in allowed:
            return False

        # Role-based restrictions: only developers or admins may move to in-progress or resolved
        if new_status in {self.STATUS_IN_PROGRESS, self.STATUS_RESOLVED}:
            if by_user is None:
                return False
            if not (by_user.is_developer() or by_user.is_admin()):
                return False

        # Assignment transitions typically require admin or developer
        if new_status == self.STATUS_ASSIGNED:
            if by_user is not None and not (by_user.is_developer() or by_user.is_admin()):
                return False

        return True


class Comment(models.Model):
    issue = models.ForeignKey(Issue, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.issue.title}"


class AuditLog(models.Model):
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"

    ACTION_CHOICES = [
        (ACTION_CREATE, "Create"),
        (ACTION_UPDATE, "Update"),
        (ACTION_DELETE, "Delete"),
    ]

    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["object_id"]),
            models.Index(fields=["changed_by"]),
        ]

    def __str__(self):
        return f"{self.model_name} {self.object_id} {self.action} at {self.timestamp}"
