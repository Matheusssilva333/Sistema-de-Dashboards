"""
Model: Campanha
Representa uma campanha de anúncios
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CampaignObjective(str, enum.Enum):
    """Objetivos de campanha possíveis"""
    OUTCOME_AWARENESS = "OUTCOME_AWARENESS"
    OUTCOME_ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    OUTCOME_LEADS = "OUTCOME_LEADS"
    OUTCOME_SALES = "OUTCOME_SALES"
    OUTCOME_TRAFFIC = "OUTCOME_TRAFFIC"
    OUTCOME_APP_PROMOTION = "OUTCOME_APP_PROMOTION"


class CampaignStatus(str, enum.Enum):
    """Status da campanha"""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"


class Campaign(Base):
    """Modelo de Campanha"""
    
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_account_id = Column(Integer, ForeignKey("ad_accounts.id"), nullable=False)
    
    # Meta Campaign Info
    campaign_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    objective = Column(String, nullable=True)
    status = Column(String, default=CampaignStatus.ACTIVE.value)
    
    # Budget
    daily_budget = Column(Float, nullable=True)
    lifetime_budget = Column(Float, nullable=True)
    
    # Performance Summary (cache dos insights)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    
    # Calculated Metrics
    cpc = Column(Float, default=0.0)  # Cost per click
    cpm = Column(Float, default=0.0)  # Cost per thousand impressions
    ctr = Column(Float, default=0.0)  # Click-through rate
    
    # Dates
    start_time = Column(DateTime, nullable=True)
    stop_time = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    ad_account = relationship("AdAccount", back_populates="campaigns")
    ad_sets = relationship("AdSet", back_populates="campaign", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Campaign {self.campaign_id} - {self.name}>"
