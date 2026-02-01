"""
Script de Sincronização de Dados
Sincroniza dados da Meta Ads API para o banco de dados
"""
import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.ad_account import AdAccount
from app.models.campaign import Campaign
from app.models.insight import Insight
from app.services.meta_api import MetaAdsService
from app.config import settings

def sync_accounts():
    """Sincroniza contas de anúncios"""
    db = SessionLocal()
    try:
        print("📊 Sincronizando contas de anúncios...")
        
        service = MetaAdsService()
        accounts_data = service.get_ad_accounts()
        
        for acc_data in accounts_data:
            account = db.query(AdAccount).filter(
                AdAccount.account_id == acc_data['account_id']
            ).first()
            
            if account:
                # Atualizar
                account.name = acc_data['name']
                account.amount_spent = acc_data['amount_spent']
                account.balance = acc_data['balance']
                account.last_synced_at = datetime.now()
                print(f"  ✅ Atualizada conta: {account.name}")
            else:
                # Criar
                account = AdAccount(
                    user_id=1,
                    **acc_data,
                    last_synced_at=datetime.now()
                )
                db.add(account)
                print(f"  ➕ Nova conta: {acc_data['name']}")
        
        db.commit()
        print(f"✅ {len(accounts_data)} contas sincronizadas\n")
        
    except Exception as e:
        print(f"❌ Erro ao sincronizar contas: {e}")
        db.rollback()
    finally:
        db.close()

def sync_campaigns(account_id: str = None):
    """Sincroniza campanhas"""
    db = SessionLocal()
    try:
        service = MetaAdsService()
        
        # Buscar contas
        accounts = db.query(AdAccount).all()
        if account_id:
            accounts = [a for a in accounts if a.account_id == account_id]
        
        for account in accounts:
            print(f"📢 Sincronizando campanhas da conta: {account.name}")
            
            campaigns_data = service.get_campaigns(account.account_id)
            
            for camp_data in campaigns_data:
                campaign = db.query(Campaign).filter(
                    Campaign.campaign_id == camp_data['campaign_id']
                ).first()
                
                if campaign:
                    # Atualizar
                    campaign.name = camp_data['name']
                    campaign.status = camp_data['status']
                    campaign.last_synced_at = datetime.now()
                    print(f"  ✅ Atualizada campanha: {campaign.name}")
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
                        last_synced_at=datetime.now()
                    )
                    db.add(campaign)
                    print(f"  ➕ Nova campanha: {camp_data['name']}")
            
            db.commit()
            print(f"✅ {len(campaigns_data)} campanhas sincronizadas\n")
            
    except Exception as e:
        print(f"❌ Erro ao sincronizar campanhas: {e}")
        db.rollback()
    finally:
        db.close()

def sync_insights(days: int = 30):
    """Sincroniza insights/métricas"""
    db = SessionLocal()
    try:
        service = MetaAdsService()
        
        # Buscar campanhas ativas
        campaigns = db.query(Campaign).filter(
            Campaign.status == 'ACTIVE'
        ).all()
        
        date_start = datetime.now() - timedelta(days=days)
        
        for campaign in campaigns:
            print(f"📈 Sincronizando insights: {campaign.name}")
            
            try:
                insights_data = service.get_campaign_insights(
                    campaign.campaign_id,
                    date_start=date_start
                )
                
                for insight_data in insights_data:
                    insight_date = datetime.strptime(insight_data['date'], '%Y-%m-%d').date()
                    
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
                
                # Atualizar métricas agregadas da campanha
                total_impressions = sum(i.get('impressions', 0) for i in insights_data)
                total_clicks = sum(i.get('clicks', 0) for i in insights_data)
                total_spend = sum(i.get('spend', 0) for i in insights_data)
                
                campaign.impressions = total_impressions
                campaign.clicks = total_clicks
                campaign.spend = total_spend
                
                if total_impressions > 0:
                    campaign.ctr = (total_clicks / total_impressions) * 100
                    campaign.cpm = (total_spend / total_impressions) * 1000
                
                if total_clicks > 0:
                    campaign.cpc = total_spend / total_clicks
                
                db.commit()
                print(f"  ✅ {len(insights_data)} insights sincronizados")
                
            except Exception as e:
                print(f"  ⚠️  Erro ao sincronizar insights: {e}")
                continue
        
        print(f"\n✅ Sincronização de insights concluída\n")
        
    except Exception as e:
        print(f"❌ Erro ao sincronizar insights: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Executa sincronização completa"""
    print("=" * 60)
    print("🔄 SINCRONIZAÇÃO DE DADOS - META ADS")
    print("=" * 60)
    print()
    
    # Verificar token
    if not settings.META_ACCESS_TOKEN:
        print("❌ Token de acesso não configurado!")
        print("💡 Configure META_ACCESS_TOKEN no arquivo .env")
        return
    
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"⏰ Período: Últimos {settings.DEFAULT_DATA_RANGE} dias")
    print()
    
    # Sincronizar
    sync_accounts()
    sync_campaigns()
    sync_insights(settings.DEFAULT_DATA_RANGE)
    
    print("=" * 60)
    print("🎉 SINCRONIZAÇÃO CONCLUÍDA!")
    print("=" * 60)

if __name__ == "__main__":
    main()
