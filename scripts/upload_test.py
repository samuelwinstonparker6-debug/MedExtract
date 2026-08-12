import os
import sys
import time

URL = 'http://127.0.0.1:8000/api/v2/documents/upload'
FILE = 'tests/fraud_samples/auth_city_hosp.png'
SOURCE = 'hospital'

if not os.path.exists(FILE):
    print('File not found:', FILE)
    sys.exit(2)

# Try requests first, then httpx
try:
    import requests
    files = {'file': ('auth_city_hosp.png', open(FILE, 'rb'), 'image/png')}
    data = {'source_type': SOURCE}
    print('Uploading via requests...')
    r = requests.post(URL, files=files, data=data)
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    try:
        import httpx
        print('Uploading via httpx...')
        with httpx.Client() as client:
            with open(FILE, 'rb') as f:
                r = client.post(URL, files={'file': ('auth_city_hosp.png', f, 'image/png')}, data={'source_type': SOURCE})
            print('Status:', r.status_code)
            print('Response:', r.text)
    except Exception as e2:
        print('Both requests and httpx failed:', e, e2)
        sys.exit(1)

# If upload succeeded, try to parse ID and poll status
import json
try:
    doc = r.json()
    doc_id = doc.get('id')
    if not doc_id:
        print('No doc id in response')
        sys.exit(0)
    print('Uploaded document id:', doc_id)
    # Poll for status
    for i in range(30):
        try:
            rr = requests.get(f'http://127.0.0.1:8000/api/v2/documents/{doc_id}')
            if rr.status_code == 200:
                d = rr.json()
                print('Poll', i, 'status=', d.get('status'), 'fraud_status=', d.get('fraud_status'))
                if d.get('status') in ('completed', 'failed'):
                    break
        except Exception:
            pass
        time.sleep(1)
except Exception as e:
    print('Error parsing response:', e)

print('Done')
