from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IssuePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_admin():
            return True
        if request.method == "DELETE":
            return False
        return obj.reporter == request.user or obj.assignee == request.user


class CommentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_admin() or obj.author == request.user


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class AuditAccessPermission(permissions.BasePermission):
    """Admins have full access. Developers can list/read logs for issues assigned to them. Reporters have no access."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_admin():
            return True
        # allow developers to GET/list, but no write operations
        if user.is_developer() and request.method in permissions.SAFE_METHODS:
            return True
        return False
