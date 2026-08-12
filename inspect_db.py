import sqlite3, json

conn = sqlite3.connect('medextract.db')
cursor = conn.cursor()
cursor.execute('SELECT id, filename, source_type, document_type, structured_data, fraud_status, fraud_flags FROM documents')
rows = cursor.fetchall()
print(f"Total documents: {len(rows)}")
for r in rows:
    print("="*60)
    print(f"Doc ID: {r[0]} | File: {r[1]} | Source: {r[2]} | Type: {r[3]} | Fraud: {r[5]}")
    sd = json.loads(r[4]) if r[4] else {}
    print("Provider:", sd.get("provider_name") or sd.get("hospital_name") or sd.get("doctor_name"))
    print("Patient:", sd.get("patient_name"))
    print("Flags:", r[6])
