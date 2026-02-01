"""
Router: Relatórios
Gerencia exportação e geração de relatórios
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import logging
from io import BytesIO
import pandas as pd

from app.database import get_db
from app.models.campaign import Campaign
from app.models.insight import Insight

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/export/excel")
async def export_excel(
    campaign_id: str = Query(..., description="ID da campanha"),
    db: Session = Depends(get_db)
):
    """
    Exporta dados de uma campanha para Excel
    """
    try:
        campaign = db.query(Campaign).filter(
            Campaign.campaign_id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
        # Buscar insights
        insights = db.query(Insight).filter(
            Insight.campaign_id == campaign.id
        ).order_by(Insight.date).all()
        
        if not insights:
            raise HTTPException(status_code=404, detail="Nenhum dado disponível")
        
        # Criar DataFrame
        data = []
        for insight in insights:
            data.append({
                'Data': insight.date.isoformat(),
                'Impressões': insight.impressions,
                'Cliques': insight.clicks,
                'Gasto (R$)': round(insight.spend, 2),
                'Alcance': insight.reach,
                'Conversões': insight.conversions,
                'CTR (%)': round(insight.ctr, 2),
                'CPC (R$)': round(insight.cpc, 2),
                'CPM (R$)': round(insight.cpm, 2),
                'ROAS': round(insight.roas, 2) if insight.roas else 0
            })
        
        df = pd.DataFrame(data)
        
        # Criar arquivo Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Métricas', index=False)
        
        output.seek(0)
        
        filename = f"relatorio_{campaign.name.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    
    except Exception as e:
        logger.error(f"Erro ao exportar Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
async def export_csv(
    campaign_id: str = Query(..., description="ID da campanha"),
    db: Session = Depends(get_db)
):
    """
    Exporta dados de uma campanha para CSV
    """
    try:
        campaign = db.query(Campaign).filter(
            Campaign.campaign_id == campaign_id
        ).first()
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")
        
        # Buscar insights
        insights = db.query(Insight).filter(
            Insight.campaign_id == campaign.id
        ).order_by(Insight.date).all()
        
        if not insights:
            raise HTTPException(status_code=404, detail="Nenhum dado disponível")
        
        # Criar DataFrame
        data = []
        for insight in insights:
            data.append({
                'Data': insight.date.isoformat(),
                'Impressões': insight.impressions,
                'Cliques': insight.clicks,
                'Gasto (R$)': round(insight.spend, 2),
                'Alcance': insight.reach,
                'Conversões': insight.conversions,
                'CTR (%)': round(insight.ctr, 2),
                'CPC (R$)': round(insight.cpc, 2),
                'CPM (R$)': round(insight.cpm, 2),
            })
        
        df = pd.DataFrame(data)
        
        # Criar CSV em memória
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        filename = f"relatorio_{campaign.name.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
        
        return StreamingResponse(
            output,
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    
    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
