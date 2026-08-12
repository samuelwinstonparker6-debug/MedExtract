from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class TemplateMatch(Base):
    __tablename__ = "template_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id_1 = Column(Integer, index=True)
    document_id_2 = Column(Integer, index=True)
    similarity_score = Column(Float, nullable=False)
    flag_level = Column(String, default="NONE")  # NONE, AMBER, RED
    provider_name_1 = Column(String, nullable=True)
    provider_name_2 = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
