import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
import os

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # clean up test db file
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except:
            pass

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_upload_document_success():
    # Create a dummy PDF file
    file_content = b"%PDF-1.4 dummy pdf content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    data = {"source_type": "lab"}
    
    response = client.post("/api/v2/documents/upload", files=files, data=data)
    
    assert response.status_code in [200, 202]
    res_data = response.json()
    assert res_data["filename"] == "test.pdf"
    assert res_data["source_type"] == "lab"
    assert res_data["status"] == "pending"
    assert "id" in res_data
    
    # Check status endpoint
    doc_id = res_data["id"]
    status_response = client.get(f"/api/v2/documents/{doc_id}")
    assert status_response.status_code == 200
    assert status_response.json()["id"] == doc_id

def test_upload_document_invalid_type():
    file_content = b"dummy text content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    data = {"source_type": "lab"}
    
    response = client.post("/api/v2/documents/upload", files=files, data=data)
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]

def test_upload_document_invalid_source():
    file_content = b"%PDF-1.4 dummy pdf content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    data = {"source_type": "alien"}
    
    response = client.post("/api/v2/documents/upload", files=files, data=data)
    
    assert response.status_code == 400
    assert "source_type must be one of" in response.json()["detail"]

