import os, sys
sys.path.append(r'C:\Users\jainm\Videos\Desktop\Projects\PEP_Project\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','issue_tracker.settings')
import django
django.setup()
from tracker.models import User, Issue, AuditLog

# prepare users
reporter, _ = User.objects.get_or_create(username='audit_reporter', defaults={'email':'rep@example.com','role':User.ROLE_REPORTER})
dev, _ = User.objects.get_or_create(username='audit_dev', defaults={'email':'dev@example.com','role':User.ROLE_DEVELOPER})

# create issue with changed_by attached
issue = Issue(title='Audit Issue', description='Testing audit logs', reporter=reporter)
issue._changed_by = reporter
issue.save()
print('Created issue id', issue.id)

# update status as developer
issue._changed_by = dev
issue.status = Issue.STATUS_IN_PROGRESS
issue.save()

# fetch audit logs
logs = AuditLog.objects.filter(model_name='Issue', object_id=str(issue.id)).order_by('timestamp')
for l in logs:
    print(l.timestamp, l.action, l.changed_by and l.changed_by.username, l.changes)
