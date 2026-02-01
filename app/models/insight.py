"""
Model: Insights/Métricas
Armazena dados de performance detalhados por dia
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Insight(Base):
    """Modelo de Insights/Métricas"""
    
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    
    # Date
    date = Column(Date, nullable=False, index=True)
    
    # Basic Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    frequency = Column(Float, default=0.0)
    
    # Engagement
    post_engagement = Column(Integer, default=0)
    post_reactions = Column(Integer, default=0)
    post_comments = Column(Integer, default=0)
    post_shares = Column(Integer, default=0)
    
    # Video Metrics (if applicable)
    video_views = Column(Integer, default=0)
    video_views_p25 = Column(Integer, default=0)
    video_views_p50 = Column(Integer, default=0)
    video_views_p75 = Column(Integer, default=0)
    video_views_p100 = Column(Integer, default=0)
    
    # Conversions
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0.0)
    
    # Purchase (if applicable)
    purchases = Column(Integer, default=0)
    purchase_value = Column(Float, default=0.0)
    
    # Leads (if applicable)
    leads = Column(Integer, default=0)
    
    # Cost Metrics (calculated)
    cpc = Column(Float, default=0.0)  # Cost per click
    cpm = Column(Float, default=0.0)  # Cost per thousand impressions
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpa = Column(Float, default=0.0)  # Cost per acquisition
    roas = Column(Float, default=0.0)  # Return on ad spend
    
    # Link Clicks
    link_clicks = Column(Integer, default=0)
    unique_link_clicks = Column(Integer, default=0)
    
    # Placement
    placement = Column(String, nullable=True)  # feed, stories, reels, etc.
    
    # Device
    device = Column(String, nullable=True)  # mobile, desktop
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="insights")
    
    # Indexes compostos para queries otimizadas
    __table_args__ = (
        Index('idx_campaign_date', 'campaign_id', 'date'),
        Index('idx_date_campaign', 'date', 'campaign_id'),
    )
    
    def __repr__(self):
        return f"<Insight Campaign {self.campaign_id} - {self.date}>"
