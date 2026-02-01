"""
Router: Insights/Métricas
Gerencia insights e análises de performance
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models.campaign import Campaign
from app.models.insight import Insight
from app.services.meta_api import MetaAdsService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/campaign/{campaign_id}")
async def get_campaign_insights(
    campaign_id: str,
    date_start: Optional[str] = Query(None, description="Data inicial (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="Data final (YYYY-MM-DD)"),
    sync: bool = Query(False, description="Sincronizar com API antes de retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtém insights de uma campanha
    """
    try:
        campaign = db.query(Campaign).filter(
            Campaign.campaign_id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
        # Sincronizar se solicitado
        if sync:
            service = MetaAdsService()
            
            start_date = datetime.strptime(date_start, '%Y-%m-%d') if date_start else None
            end_date = datetime.strptime(date_end, '%Y-%m-%d') if date_end else None
            
            insights_data = service.get_campaign_insights(
                campaign_id,
                date_start=start_date,
                date_end=end_date
            )
            
            # Salvar insights no banco
            for insight_data in insights_data:
                insight_date = datetime.strptime(insight_data['date'], '%Y-%m-%d').date()
                
                # Verificar se já existe
                insight = db.query(Insight).filter(
                    Insight.campaign_id == campaign.id,
                    Insight.date == insight_date
                ).first()
                
                if insight:
                    # Atualizar
                    for key, value in insight_data.items():
                        if key != 'date' and hasattr(insight, key):
                            setattr(insight, key, value)
                else:
                    # Criar
                    insight = Insight(
                        campaign_id=campaign.id,
                        date=insight_date,
                        **{k: v for k, v in insight_data.items() if k != 'date'}
                    )
                    db.add(insight)
            
            db.commit()
        
        # Buscar do banco
        query = db.query(Insight).filter(Insight.campaign_id == campaign.id)
        
        if date_start:
            query = query.filter(Insight.date >= datetime.strptime(date_start, '%Y-%m-%d').date())
        if date_end:
            query = query.filter(Insight.date <= datetime.strptime(date_end, '%Y-%m-%d').date())
        
        query = query.order_by(Insight.date.desc())
        insights = query.all()
        
        # Calcular totais
        total_impressions = sum(i.impressions for i in insights)
        total_clicks = sum(i.clicks for i in insights)
        total_spend = sum(i.spend for i in insights)
        total_conversions = sum(i.conversions for i in insights)
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        
        return {
            "campaign": {
                "id": campaign.campaign_id,
                "name": campaign.name
            },
            "period": {
                "start": date_start or insights[-1].date.isoformat() if insights else None,
                "end": date_end or insights[0].date.isoformat() if insights else None,
                "days": len(insights)
            },
            "totals": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "spend": round(total_spend, 2),
                "conversions": total_conversions,
                "ctr": round(avg_ctr, 2),
                "cpc": round(avg_cpc, 2),
                "cpm": round(avg_cpm, 2)
            },
            "daily_data": [
                {
                    "date": i.date.isoformat(),
                    "impressions": i.impressions,
                    "clicks": i.clicks,
                    "spend": round(i.spend, 2),
                    "reach": i.reach,
                    "conversions": i.conversions,
                    "ctr": round(i.ctr, 2),
                    "cpc": round(i.cpc, 2),
                    "cpm": round(i.cpm, 2),
                    "roas": round(i.roas, 2) if i.roas else 0
                }
                for i in insights
            ]
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_summary(
    account_id: Optional[str] = Query(None),
    days: int = Query(30, description="Últimos N dias"),
    db: Session = Depends(get_db)
):
    """
    Obtém resumo geral de performance
    """
    try:
        # Data de corte
        date_cutoff = datetime.now().date() - timedelta(days=days)
        
        # Query base
        query = db.query(
            func.sum(Insight.impressions).label('total_impressions'),
            func.sum(Insight.clicks).label('total_clicks'),
            func.sum(Insight.spend).label('total_spend'),
            func.sum(Insight.conversions).label('total_conversions'),
            func.count(func.distinct(Insight.campaign_id)).label('campaigns_count')
        ).filter(Insight.date >= date_cutoff)
        
        # Filtrar por conta se fornecido
        if account_id:
            query = query.join(Campaign).join(AdAccount).filter(
                AdAccount.account_id == account_id
            )
        
        result = query.first()
        
        total_impressions = result.total_impressions or 0
        total_clicks = result.total_clicks or 0
        total_spend = result.total_spend or 0
        total_conversions = result.total_conversions or 0
        campaigns_count = result.campaigns_count or 0
        
        return {
            "period_days": days,
            "campaigns_count": campaigns_count,
            "metrics": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "spend": round(total_spend, 2),
                "conversions": total_conversions,
                "ctr": round((total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2),
                "cpc": round((total_spend / total_clicks) if total_clicks > 0 else 0, 2),
                "cpm": round((total_spend / total_impressions * 1000) if total_impressions > 0 else 0, 2),
                "cpa": round((total_spend / total_conversions) if total_conversions > 0 else 0, 2)
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter resumo: {e}")
        raise HTTPException(status_code=500, detail=str(e))
