import os, sys
sys.path.append(r'C:\Users\jainm\Videos\Desktop\Projects\PEP_Project\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','issue_tracker.settings')
import django
django.setup()
from rest_framework.test import APIRequestFactory, force_authenticate
from tracker.views import AuditLogViewSet
from tracker.models import User

factory = APIRequestFactory()
admin, _ = User.objects.get_or_create(username='api_admin', defaults={'email':'admin@example.com','role':User.ROLE_ADMIN})
request = factory.get('/api/audit-logs/')
view = AuditLogViewSet.as_view({'get':'list'})
force_authenticate(request, user=admin)
response = view(request)
print('Status:', response.status_code)
print(response.data if hasattr(response, 'data') else response)
