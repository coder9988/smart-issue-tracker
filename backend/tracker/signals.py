from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Issue, AuditLog
from django.forms.models import model_to_dict

@receiver(pre_save, sender=Issue)
def capture_issue_pre_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Issue.objects.get(pk=instance.pk)
            instance._pre_save_snapshot = model_to_dict(old, fields=["title","description","category","priority","status","assignee_id"])
        except Issue.DoesNotExist:
            instance._pre_save_snapshot = None
    else:
        instance._pre_save_snapshot = None

@receiver(post_save, sender=Issue)
def capture_issue_post_save(sender, instance, created, **kwargs):
    changed_by = getattr(instance, "_changed_by", None)
    if created:
        AuditLog.objects.create(
            model_name="Issue",
            object_id=str(instance.pk),
            action=AuditLog.ACTION_CREATE,
            changed_by=changed_by,
            changes=model_to_dict(instance, fields=["title","description","category","priority","status","assignee_id"]),
        )
    else:
        before = getattr(instance, "_pre_save_snapshot", {}) or {}
        after = model_to_dict(instance, fields=["title","description","category","priority","status","assignee_id"]) or {}
        diffs = {}
        for k, v in after.items():
            old_v = before.get(k)
            if old_v != v:
                diffs[k] = {"from": old_v, "to": v}
        if diffs:
            AuditLog.objects.create(
                model_name="Issue",
                object_id=str(instance.pk),
                action=AuditLog.ACTION_UPDATE,
                changed_by=changed_by,
                changes=diffs,
            )

@receiver(post_delete, sender=Issue)
def capture_issue_delete(sender, instance, **kwargs):
    changed_by = getattr(instance, "_changed_by", None)
    AuditLog.objects.create(
        model_name="Issue",
        object_id=str(instance.pk),
        action=AuditLog.ACTION_DELETE,
        changed_by=changed_by,
        changes=None,
    )
