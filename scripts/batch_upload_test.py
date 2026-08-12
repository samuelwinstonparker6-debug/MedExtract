import os
import sys
import time
import json
import argparse

import requests

BASE_URL = os.environ.get('MEDEXTRACT_API', 'http://127.0.0.1:8000')
UPLOAD_URL = f"{BASE_URL}/api/v2/documents/upload"
GET_URL = f"{BASE_URL}/api/v2/documents/{{}}"


def upload_file(path, source_type='hospital'):
    with open(path, 'rb') as f:
        files = {'file': (os.path.basename(path), f, 'image/png')}
        data = {'source_type': source_type}
        r = requests.post(UPLOAD_URL, files=files, data=data)
    return r


def poll_document(doc_id, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(GET_URL.format(doc_id))
            if r.status_code == 200:
                d = r.json()
                status = d.get('status')
                if status in ('completed', 'failed'):
                    return d
        except Exception:
            pass
        time.sleep(1)
    return None


def main():
    parser = argparse.ArgumentParser(description='Batch upload images and collect fraud QA report')
    parser.add_argument('input', help='File or directory of images to upload')
    parser.add_argument('--source', default='hospital', choices=['hospital','doctor','lab'], help='source_type for uploads')
    parser.add_argument('--out', default='scripts/qa_report.json', help='Output report path')
    parser.add_argument('--timeout', type=int, default=90, help='Per-document poll timeout seconds')
    args = parser.parse_args()

    paths = []
    if os.path.isdir(args.input):
        for root, dirs, files in os.walk(args.input):
            for fn in files:
                if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf', '.webp', '.jfif')):
                    paths.append(os.path.join(root, fn))
    elif os.path.isfile(args.input):
        paths = [args.input]
    else:
        print('Input not found:', args.input)
        sys.exit(2)

    report = []
    for p in sorted(paths):
        print(f'Uploading {p} ...')
        start = time.time()
        try:
            r = upload_file(p, source_type=args.source)
        except Exception as e:
            print('Upload failed:', e)
            report.append({'file': p, 'error': str(e)})
            continue

        entry = {'file': p, 'status_code': r.status_code}
        try:
            j = r.json()
            entry.update({'response': j})
        except Exception:
            entry.update({'response_text': r.text})

        if r.status_code == 202 and isinstance(j, dict) and j.get('id'):
            doc_id = j['id']
            entry['doc_id'] = doc_id
            print('Polling document id', doc_id)
            d = poll_document(doc_id, timeout=args.timeout)
            if d:
                entry['final'] = {
                    'status': d.get('status'),
                    'fraud_status': d.get('fraud_status'),
                    'fraud_score': d.get('fraud_score'),
                    'fraud_flags': d.get('fraud_flags'),
                }
            else:
                entry['final'] = {'status': 'timeout'}
        else:
            entry['doc_id'] = None

        entry['time_taken'] = time.time() - start
        report.append(entry)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print('Report written to', args.out)


if __name__ == '__main__':
    main()
