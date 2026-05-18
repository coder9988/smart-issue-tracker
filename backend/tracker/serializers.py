from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Issue, Comment, AuditLog


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]

    def get_role(self, obj):
        if obj.is_admin():
            return User.ROLE_ADMIN
        return obj.role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        role = attrs.get("role", User.ROLE_REPORTER)
        if role == User.ROLE_ADMIN:
            raise serializers.ValidationError({"role": "Admin registration is not allowed via the public API."})
        if role not in [User.ROLE_DEVELOPER, User.ROLE_REPORTER]:
            raise serializers.ValidationError({"role": "Invalid role. Must be 'developer' or 'reporter'."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "issue", "author", "body", "created_at"]
        read_only_fields = ["author", "created_at"]


class IssueSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.ROLE_DEVELOPER),
        source="assignee",
        write_only=True,
        required=False,
    )
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "reporter",
            "assignee",
            "assignee_id",
            "created_at",
            "updated_at",
            "comments",
        ]
        read_only_fields = ["reporter", "created_at", "updated_at", "comments"]

    def create(self, validated_data):
        request = self.context.get("request")
        changed_by = None
        if request is not None:
            changed_by = request.user
        validated_data["reporter"] = request.user if request is not None else None
        if validated_data.get("assignee") and validated_data.get("status", Issue.STATUS_OPEN) == Issue.STATUS_OPEN:
            validated_data["status"] = Issue.STATUS_ASSIGNED

        # create instance so we can attach _changed_by before saving
        issue = Issue(**validated_data)
        if changed_by:
            issue._changed_by = changed_by
        issue.save()
        return issue

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        new_status = validated_data.get("status")
        if "assignee" in validated_data and instance.status == Issue.STATUS_OPEN and new_status in [None, Issue.STATUS_OPEN]:
            validated_data["status"] = Issue.STATUS_ASSIGNED
            new_status = Issue.STATUS_ASSIGNED
        if new_status and new_status != instance.status:
            if not instance.can_transition_to(new_status, by_user=user):
                raise serializers.ValidationError({"status": ["Invalid or unauthorized status transition."]})

        # attach user for audit logging
        if user is not None:
            instance._changed_by = user

        return super().update(instance, validated_data)


class AuditLogSerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)
    issue_id = serializers.SerializerMethodField()
    changes_list = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ["id", "model_name", "object_id", "issue_id", "action", "changed_by", "changes", "changes_list", "timestamp"]
        read_only_fields = fields

    def get_issue_id(self, obj):
        if obj.model_name.lower() == "issue":
            try:
                return int(obj.object_id)
            except Exception:
                return obj.object_id
        return None

    def get_changes_list(self, obj):
        changes = obj.changes or {}
        out = []
        if isinstance(changes, dict):
            for field, val in changes.items():
                if isinstance(val, dict) and ("from" in val or "to" in val):
                    out.append({"field": field, "from": val.get("from"), "to": val.get("to")})
                else:
                    out.append({"field": field, "value": val})
        return out
