"""
Router: Campanhas
Gerencia campanhas de anúncios
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from datetime import datetime

from app.database import get_db
from app.models.campaign import Campaign
from app.models.ad_account import AdAccount
from app.services.meta_api import MetaAdsService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def list_campaigns(
    account_id: Optional[str] = Query(None, description="ID da conta de anúncios"),
    status: Optional[str] = Query(None, description="Status (ACTIVE, PAUSED, etc)"),
    db: Session = Depends(get_db)
):
    """
    Lista campanhas
    Se account_id for fornecido, sincroniza com a API
    """
    try:
        # Se account_id fornecido, sincronizar
        if account_id:
            account = db.query(AdAccount).filter(
                AdAccount.account_id == account_id
            ).first()
            
            if not account:
                raise HTTPException(status_code=404, detail="Conta não encontrada")
            
            # Sincronizar campanhas
            service = MetaAdsService()
            status_filter = [status] if status else None
            campaigns_data = service.get_campaigns(account_id, status_filter)
            
            # Salvar/atualizar no banco
            for camp_data in campaigns_data:
                campaign = db.query(Campaign).filter(
                    Campaign.campaign_id == camp_data['campaign_id']
                ).first()
                
                if campaign:
                    # Atualizar
                    campaign.name = camp_data['name']
                    campaign.status = camp_data['status']
                    campaign.objective = camp_data['objective']
                    campaign.daily_budget = camp_data['daily_budget']
                    campaign.lifetime_budget = camp_data['lifetime_budget']
                    campaign.last_synced_at = datetime.now()
                else:
                    # Criar
                    campaign = Campaign(
                        ad_account_id=account.id,
                        campaign_id=camp_data['campaign_id'],
                        name=camp_data['name'],
                        status=camp_data['status'],
                        objective=camp_data['objective'],
                        daily_budget=camp_data['daily_budget'],
                        lifetime_budget=camp_data['lifetime_budget'],
                        start_time=datetime.fromisoformat(camp_data['start_time'].replace('Z', '+00:00')) if camp_data.get('start_time') else None,
                        stop_time=datetime.fromisoformat(camp_data['stop_time'].replace('Z', '+00:00')) if camp_data.get('stop_time') else None,
                        last_synced_at=datetime.now()
                    )
                    db.add(campaign)
            
            db.commit()
        
        # Buscar do banco
        query = db.query(Campaign)
        
        if account_id:
            account = db.query(AdAccount).filter(AdAccount.account_id == account_id).first()
            if account:
                query = query.filter(Campaign.ad_account_id == account.id)
        
        if status:
            query = query.filter(Campaign.status == status)
        
        campaigns = query.all()
        
        return {
            "count": len(campaigns),
            "campaigns": [
                {
                    "id": c.id,
                    "campaign_id": c.campaign_id,
                    "name": c.name,
                    "objective": c.objective,
                    "status": c.status,
                    "daily_budget": c.daily_budget,
                    "lifetime_budget": c.lifetime_budget,
                    "impressions": c.impressions,
                    "clicks": c.clicks,
                    "spend": c.spend,
                    "ctr": c.ctr,
                    "cpc": c.cpc,
                    "cpm": c.cpm,
                    "conversions": c.conversions,
                    "start_time": c.start_time,
                    "stop_time": c.stop_time,
                    "last_synced_at": c.last_synced_at
                }
                for c in campaigns
            ]
        }
    
    except Exception as e:
        logger.error(f"Erro ao listar campanhas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """
    Obtém detalhes de uma campanha específica
    """
    campaign = db.query(Campaign).filter(
        Campaign.campaign_id == campaign_id
    ).first()
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    return {
        "id": campaign.id,
        "campaign_id": campaign.campaign_id,
        "name": campaign.name,
        "objective": campaign.objective,
        "status": campaign.status,
        "daily_budget": campaign.daily_budget,
        "lifetime_budget": campaign.lifetime_budget,
        "impressions": campaign.impressions,
        "clicks": campaign.clicks,
        "spend": campaign.spend,
        "reach": campaign.reach,
        "conversions": campaign.conversions,
        "ctr": campaign.ctr,
        "cpc": campaign.cpc,
        "cpm": campaign.cpm,
        "start_time": campaign.start_time,
        "stop_time": campaign.stop_time,
        "ad_sets_count": len(campaign.ad_sets),
        "insights_count": len(campaign.insights),
        "last_synced_at": campaign.last_synced_at
    }


@router.post("/{campaign_id}/sync")
async def sync_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """
    Sincroniza uma campanha específica com a Meta API
    """
    try:
        campaign = db.query(Campaign).filter(
            Campaign.campaign_id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
        # Buscar insights
        service = MetaAdsService()
        insights_data = service.get_campaign_insights(campaign_id)
        
        # Atualizar métricas agregadas da campanha
        total_impressions = sum(i.get('impressions', 0) for i in insights_data)
        total_clicks = sum(i.get('clicks', 0) for i in insights_data)
        total_spend = sum(i.get('spend', 0) for i in insights_data)
        total_reach = max((i.get('reach', 0) for i in insights_data), default=0)
        total_conversions = sum(i.get('conversions', 0) for i in insights_data)
        
        campaign.impressions = total_impressions
        campaign.clicks = total_clicks
        campaign.spend = total_spend
        campaign.reach = total_reach
        campaign.conversions = total_conversions
        
        # Calcular métricas
        if total_impressions > 0:
            campaign.ctr = (total_clicks / total_impressions) * 100
            campaign.cpm = (total_spend / total_impressions) * 1000
        
        if total_clicks > 0:
            campaign.cpc = total_spend / total_clicks
        
        campaign.last_synced_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Campanha {campaign.name} sincronizada",
            "insights_count": len(insights_data),
            "metrics": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "spend": total_spend,
                "ctr": campaign.ctr,
                "cpc": campaign.cpc
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao sincronizar campanha: {e}")
        raise HTTPException(status_code=500, detail=str(e))
