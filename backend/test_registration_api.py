import urllib.request
import urllib.error
import json

url = 'http://127.0.0.1:8000/api/register/register/'
data = json.dumps({
    'username': 'testuser123',
    'email': 'testuser123@example.com',
    'password': 'Testpass123!',
    'role': 'reporter',
}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print('STATUS', resp.status)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode())
except Exception as e:
    print('ERR', e)
