from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.domain import Document
from collections import defaultdict
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    
    total_docs = len(documents)
    docs_by_type = defaultdict(int)
    docs_by_source = defaultdict(int)
    
    total_processing_time_seconds = 0
    docs_processed_count = 0
    
    total_confidence = 0.0
    confidence_field_count = 0
    
    # Last 7 days volume
    volume_over_time_map = defaultdict(int)
    today = datetime.now().date()
    for i in range(7):
        day = today - timedelta(days=6-i)
        volume_over_time_map[day.strftime('%b %d')] = 0
        
    fraud_stats = {"NONE": 0, "AMBER": 0, "RED": 0}

    for doc in documents:
        # Document Types
        doc_type = doc.document_type if doc.document_type else "unknown"
        docs_by_type[doc_type] += 1
        
        # Sources
        source_val = doc.source_type if doc.source_type else "unknown"
        docs_by_source[source_val] += 1
        
        # Fraud Stats
        f_status = getattr(doc, 'fraud_status', 'NONE')
        if not f_status:
            f_status = 'NONE'
        fraud_stats[f_status] += 1
        
        # Volume over time
        if doc.upload_timestamp:
            upload_date = doc.upload_timestamp.date()
            if (today - upload_date).days < 7 and upload_date <= today:
                volume_over_time_map[upload_date.strftime('%b %d')] += 1
                
        # Processing time
        if doc.completed_timestamp and doc.upload_timestamp and doc.status == "extracted":
            delta = doc.completed_timestamp - doc.upload_timestamp
            total_processing_time_seconds += delta.total_seconds()
            docs_processed_count += 1
            
        # Confidence score
        if doc.structured_data:
            for field, data in doc.structured_data.items():
                if isinstance(data, dict) and "confidence" in data:
                    total_confidence += data["confidence"]
                    confidence_field_count += 1

    avg_processing_time = (total_processing_time_seconds / docs_processed_count) if docs_processed_count > 0 else 0
    avg_confidence = (total_confidence / confidence_field_count) if confidence_field_count > 0 else 0

    return {
        "total_documents": total_docs,
        "documents_by_type": [{"name": str(k).capitalize(), "value": v} for k, v in docs_by_type.items()],
        "documents_by_source": [{"name": str(k).capitalize(), "value": v} for k, v in docs_by_source.items()],
        "average_processing_time_seconds": round(avg_processing_time, 2),
        "average_confidence": round(avg_confidence, 2),
        "volume_over_time": [{"date": k, "count": v} for k, v in volume_over_time_map.items()],
        "fraud_stats": fraud_stats
    }
