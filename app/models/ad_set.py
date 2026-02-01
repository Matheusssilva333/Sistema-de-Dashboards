"""
Model: Conjunto de Anúncios (Ad Set)
Representa um conjunto de anúncios dentro de uma campanha
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AdSet(Base):
    """Modelo de Conjunto de Anúncios"""
    
    __tablename__ = "ad_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    
    # Meta AdSet Info
    adset_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="ACTIVE")
    
    # Budget
    daily_budget = Column(Float, nullable=True)
    lifetime_budget = Column(Float, nullable=True)
    
    # Targeting
    targeting = Column(JSON, nullable=True)  # Dados de segmentação
    
    # Performance Summary
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    
    # Optimization
    optimization_goal = Column(String, nullable=True)
    billing_event = Column(String, nullable=True)
    bid_amount = Column(Float, nullable=True)
    
    # Dates
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="ad_sets")
    ads = relationship("Ad", back_populates="ad_set", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AdSet {self.adset_id} - {self.name}>"
