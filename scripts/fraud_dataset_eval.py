import os
import sys
import json
import time
import csv
import argparse
import requests

BASE_URL = os.environ.get('MEDEXTRACT_API', 'http://127.0.0.1:8000')
UPLOAD_URL = f"{BASE_URL}/api/v2/documents/upload"
GET_DOC_URL = f"{BASE_URL}/api/v2/documents/{{}}"
GET_SIM_URL = f"{BASE_URL}/api/v2/similarity/{{}}/similar"

DATASET_DIR = 'tests/fraud_dataset'


def upload(path, source='hospital'):
    with open(path, 'rb') as f:
        mime = 'image/png'
        if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
            mime = 'image/jpeg'
        elif path.lower().endswith('.pdf'):
            mime = 'application/pdf'
        files = {'file': (os.path.basename(path), f, mime)}
        data = {'source_type': source}
        # Respect rate limits by retrying on 429 with backoff
        backoff = 1
        for attempt in range(6):
            r = requests.post(UPLOAD_URL, files=files, data=data)
            if r.status_code != 429:
                break
            time.sleep(backoff)
            backoff = min(backoff * 2, 8)
        # small pause to avoid hitting the 20/minute limiter
        time.sleep(3)
        return r


def poll(doc_id, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(GET_DOC_URL.format(doc_id))
        if r.status_code == 200:
            d = r.json()
            if d.get('status') in ('completed', 'failed'):
                return d
        time.sleep(1)
    return None


def get_similar(doc_id):
    r = requests.get(GET_SIM_URL.format(doc_id))
    if r.status_code == 200:
        return r.json()
    return []


def resolve_path(rel):
    p = os.path.join(DATASET_DIR, rel)
    if os.path.exists(p):
        return p
    # support top-level files
    p2 = os.path.join(DATASET_DIR, os.path.basename(rel))
    if os.path.exists(p2):
        return p2
    return None


def evaluate_pair(a_rel, b_rel, expected_label, source='hospital', timeout=60):
    a_path = resolve_path(a_rel)
    b_path = resolve_path(b_rel)
    if not a_path or not b_path:
        return {'error': 'file not found', 'a_path': a_path, 'b_path': b_path}

    ra = upload(a_path, source=source)
    if ra.status_code not in (200,202):
        return {'error': 'upload A failed', 'status_code': ra.status_code, 'text': ra.text}
    a = ra.json()
    a_id = a.get('id')
    pa = poll(a_id, timeout=timeout)

    rb = upload(b_path, source=source)
    if rb.status_code not in (200,202):
        return {'error': 'upload B failed', 'status_code': rb.status_code, 'text': rb.text}
    b = rb.json()
    b_id = b.get('id')
    pb = poll(b_id, timeout=timeout)

    # fetch similarity for B and look for A
    sims = get_similar(str(b_id))
    found = None
    for s in sims:
        if str(s.get('matched_document_id')) == str(a_id) or str(s.get('matched_document_id')) == str(a.get('id')):
            found = s
            break

    similarity_score = found.get('similarity_score') if found else None
    structural_similarity = found.get('structural_similarity') if found else None
    visual_similarity = found.get('visual_similarity') if found else None
    result = {
        'a_rel': a_rel,
        'b_rel': b_rel,
        'a_id': a_id,
        'b_id': b_id,
        'a_status': (pa or {}).get('status') if pa else None,
        'b_status': (pb or {}).get('status') if pb else None,
        'a_fraud_status': (pa or {}).get('fraud_status') if pa else None,
        'b_fraud_status': (pb or {}).get('fraud_status') if pb else None,
        'a_fraud_score': (pa or {}).get('fraud_score') if pa else None,
        'b_fraud_score': (pb or {}).get('fraud_score') if pb else None,
        'expected_label': expected_label,
        'match_found': bool(found),
        'similarity_score': similarity_score,
        'structural_similarity': structural_similarity,
        'visual_similarity': visual_similarity,
        'raw_sim_results': sims,
    }
    return result


def format_bool(v):
    return bool(v)


def is_detected(result, threshold=None):
    # Use the model's fraud outputs instead of similarity alone.
    # If a threshold is provided, apply it to the fraud_score.
    if threshold is not None:
        score = result.get('a_fraud_score')
        score_b = result.get('b_fraud_score')
        if score is None and score_b is None:
            return False
        return max(filter(lambda x: x is not None, [score, score_b])) >= threshold

    status_a = (result.get('a_fraud_status') or '').upper()
    status_b = (result.get('b_fraud_status') or '').upper()
    detected_a = status_a in ('AMBER', 'RED')
    detected_b = status_b in ('AMBER', 'RED')
    return detected_a or detected_b


def compute_metrics(rows, threshold=None):
    tp = fp = tn = fn = 0
    for r in rows:
        expected = r.get('expected_label')
        if expected not in ('fraud', 'genuine'):
            continue
        detected = is_detected(r, threshold)
        if expected == 'fraud' and detected:
            tp += 1
        elif expected == 'fraud' and not detected:
            fn += 1
        elif expected == 'genuine' and detected:
            fp += 1
        elif expected == 'genuine' and not detected:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = None
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else None
    return {
        'threshold': threshold,
        'tp': tp,
        'fp': fp,
        'tn': tn,
        'fn': fn,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'accuracy': accuracy,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--labels', default=os.path.join(DATASET_DIR, 'labels.json'))
    parser.add_argument('--out', default='scripts/fraud_dataset_report.csv')
    parser.add_argument('--timeout', type=int, default=60)
    parser.add_argument('--threshold', type=float, default=None,
                        help='If set, classify a pair as detected when one document fraud_score >= threshold')
    args = parser.parse_args()

    with open(args.labels, 'r', encoding='utf-8') as f:
        labels = json.load(f)

    rows = []
    for entry in labels.get('entries', []):
        pair = entry.get('pair', [])
        if len(pair) != 2:
            continue
        a_rel, b_rel = pair
        expected = entry.get('label')
        print('Evaluating', a_rel, '<->', b_rel, 'expected', expected)
        res = evaluate_pair(a_rel, b_rel, expected, timeout=args.timeout)
        rows.append(res)

    # Write CSV summary
    keys = ['a_rel','b_rel','a_id','b_id','expected_label','match_found','similarity_score','structural_similarity','visual_similarity','a_fraud_status','a_fraud_score','b_fraud_status','b_fraud_score']
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            out = {k: r.get(k) for k in keys}
            writer.writerow(out)

    # Write evaluation summary metrics
    metrics = compute_metrics(rows, threshold=args.threshold)
    summary_path = args.out.replace('.csv', '_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as sf:
        json.dump(metrics, sf, indent=2)

    # Save full JSON report as well
    with open(args.out.replace('.csv', '.json'), 'w', encoding='utf-8') as jf:
        json.dump(rows, jf, indent=2)

    print('Reports written:', args.out, args.out.replace('.csv', '.json'), summary_path)

if __name__ == '__main__':
    main()
