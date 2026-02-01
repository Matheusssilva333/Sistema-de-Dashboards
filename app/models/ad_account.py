"""
Model: Conta de Anúncios
Representa uma conta de anúncios da Meta
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AdAccount(Base):
    """Modelo de Conta de Anúncios"""
    
    __tablename__ = "ad_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Meta Account Info
    account_id = Column(String, unique=True, index=True, nullable=False)  # act_123456
    name = Column(String, nullable=False)
    currency = Column(String, default="BRL")
    timezone_name = Column(String, default="America/Sao_Paulo")
    
    # Status
    account_status = Column(Integer, default=1)  # 1=ACTIVE, 2=DISABLED
    is_active = Column(Boolean, default=True)
    
    # Business info
    business_name = Column(String, nullable=True)
    business_id = Column(String, nullable=True)
    
    # Spending limits
    spend_cap = Column(Float, nullable=True)
    amount_spent = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="ad_accounts")
    campaigns = relationship("Campaign", back_populates="ad_account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AdAccount {self.account_id} - {self.name}>"
