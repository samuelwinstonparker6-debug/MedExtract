import httpx
import time
import os

files_to_upload = [
    ("auth_city_hosp.png", "hospital"),
    ("auth_generic_labs.png", "lab"),
    ("fraud_amber_mike.png", "hospital"),
    ("fraud_red_fake.png", "clinic")
]

base_url = "http://localhost:8000/api/documents/upload"

for filename, source_type in files_to_upload:
    filepath = os.path.join("test_documents", filename)
    print(f"Uploading {filepath}...")
    with open(filepath, "rb") as f:
        files = {'file': (filename, f, 'image/png')}
        data = {'source_type': source_type}
        res = httpx.post(base_url, files=files, data=data, timeout=120.0)
        print(res.json())
    time.sleep(2) # Give it a little time to start processing
