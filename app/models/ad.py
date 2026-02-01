"""
Model: Anúncio (Ad)
Representa um anúncio individual
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Ad(Base):
    """Modelo de Anúncio"""
    
    __tablename__ = "ads"
    
    id = Column(Integer, primary_key=True, index=True)
    adset_id = Column(Integer, ForeignKey("ad_sets.id"), nullable=False)
    
    # Meta Ad Info
    ad_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="ACTIVE")
    
    # Creative
    creative = Column(JSON, nullable=True)  # Dados do criativo (imagem, vídeo, texto)
    thumbnail_url = Column(String, nullable=True)
    preview_url = Column(String, nullable=True)
    
    # Ad Copy
    title = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    call_to_action = Column(String, nullable=True)
    link = Column(String, nullable=True)
    
    # Performance Summary
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    ad_set = relationship("AdSet", back_populates="ads")
    
    def __repr__(self):
        return f"<Ad {self.ad_id} - {self.name}>"
