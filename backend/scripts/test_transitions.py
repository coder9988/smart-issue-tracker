import os
import sys
sys.path.append(r'C:\Users\jainm\Videos\Desktop\Projects\PEP_Project\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','issue_tracker.settings')
import django
django.setup()
from tracker.models import User, Issue

reporter, _ = User.objects.get_or_create(username='test_reporter', defaults={'email':'rep@example.com','role':User.ROLE_REPORTER})
dev, _ = User.objects.get_or_create(username='test_dev', defaults={'email':'dev@example.com','role':User.ROLE_DEVELOPER})
# ensure users have usable passwords for completeness
if not reporter.has_usable_password():
    reporter.set_password('Testpass123!')
    reporter.save()
if not dev.has_usable_password():
    dev.set_password('Testpass123!')
    dev.save()

issue = Issue.objects.create(title='Sample Issue', reporter=reporter)
print('Initial status:', issue.status)
print('Reporter can -> in_progress?', issue.can_transition_to(Issue.STATUS_IN_PROGRESS, by_user=reporter))
print('Dev can -> in_progress?', issue.can_transition_to(Issue.STATUS_IN_PROGRESS, by_user=dev))
print('Reporter can -> assigned?', issue.can_transition_to(Issue.STATUS_ASSIGNED, by_user=reporter))
print('Dev can -> resolved?', issue.can_transition_to(Issue.STATUS_RESOLVED, by_user=dev))
print('Dev can -> closed?', issue.can_transition_to(Issue.STATUS_CLOSED, by_user=dev))
