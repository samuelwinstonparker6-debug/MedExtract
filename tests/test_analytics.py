import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker
from app.models.domain import Document
import os
from datetime import datetime
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

client = TestClient(app)

def test_analytics_summary():
    db = TestingSessionLocal()
    
    # Create mock documents
    doc1 = Document(
        filename="1.pdf",
        source_type="doctor",
        status="extracted",
        document_type="prescription",
        upload_timestamp=datetime(2024, 1, 1, 10, 0, 0),
        completed_timestamp=datetime(2024, 1, 1, 10, 0, 5),
        structured_data={"medicines": {"value": ["A"], "confidence": 0.8}}
    )
    doc2 = Document(
        filename="2.pdf",
        source_type="hospital",
        status="extracted",
        document_type="invoice",
        upload_timestamp=datetime(2024, 1, 1, 12, 0, 0),
        completed_timestamp=datetime(2024, 1, 1, 12, 0, 10),
        structured_data={"amount": {"value": "100", "confidence": 0.9}, "name": {"value": "John", "confidence": 0.7}}
    )
    
    db.add(doc1)
    db.add(doc2)
    db.commit()
    db.close()

    response = client.get("/api/v2/analytics/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_documents"] == 2
    
    # 5s + 10s = 15s / 2 docs = 7.5s avg processing time
    assert data["average_processing_time_seconds"] == 7.5
    
    # Confidences: 0.8, 0.9, 0.7 => 2.4 / 3 = 0.8 average confidence
    assert data["average_confidence"] == 0.8
    
    types = {item["name"]: item["value"] for item in data["documents_by_type"]}
    assert types["Prescription"] == 1
    assert types["Invoice"] == 1
    
    sources = {item["name"]: item["value"] for item in data["documents_by_source"]}
    assert sources["Doctor"] == 1
    assert sources["Hospital"] == 1
