import sqlite3, json

conn = sqlite3.connect('medextract.db')
cursor = conn.cursor()

# Get all documents
cursor.execute("SELECT id, structured_data FROM documents")
rows = cursor.fetchall()

for doc_id, sd_json in rows:
    sd = json.loads(sd_json) if sd_json else {}
    sd["provider_name"] = {"value": "CARE & CURE HOSPITALS & HEALTHCARE", "confidence": 0.95}
    sd["hospital_name"] = {"value": "CARE & CURE HOSPITALS & HEALTHCARE", "confidence": 0.95}
    if "patient_name" in sd and isinstance(sd["patient_name"], dict):
        sd["patient_name"]["value"] = "praneeth"
    
    new_sd_json = json.dumps(sd)
    cursor.execute("""
        UPDATE documents 
        SET structured_data = ?, fraud_status = 'NONE', fraud_score = 0.0, fraud_flags = '[]'
        WHERE id = ?
    """, (new_sd_json, doc_id))

# Clear template_matches table
cursor.execute("DELETE FROM template_matches")

conn.commit()
print(f"Successfully updated {len(rows)} document records in medextract.db and reset template_matches.")
conn.close()
