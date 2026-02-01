"""
Serviço de Integração com Meta Ads API
Gerencia todas as interações com a Facebook Marketing API
"""
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class MetaAdsService:
    """Serviço para integração com Meta Ads API"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Inicializa o serviço da Meta Ads API
        
        Args:
            access_token: Token de acesso (usa do settings se não fornecido)
        """
        self.access_token = access_token or settings.META_ACCESS_TOKEN
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET
        self.api_version = settings.META_API_VERSION
        
        # Inicializar API
        if self.access_token:
            FacebookAdsApi.init(
                app_id=self.app_id,
                app_secret=self.app_secret,
                access_token=self.access_token,
                api_version=self.api_version
            )
            logger.info("Meta Ads API inicializada com sucesso")
    
    def get_ad_accounts(self) -> List[Dict]:
        """
        Obtém todas as contas de anúncios do usuário
        
        Returns:
            Lista de contas de anúncios
        """
        try:
            from facebook_business.adobjects.user import User
            
            me = User(fbid='me')
            ad_accounts = me.get_ad_accounts(fields=[
                'id',
                'account_id',
                'name',
                'currency',
                'account_status',
                'amount_spent',
                'balance',
                'spend_cap',
                'business_name',
                'business',
                'timezone_name',
            ])
            
            accounts_data = []
            for account in ad_accounts:
                accounts_data.append({
                    'account_id': account.get('account_id'),
                    'name': account.get('name'),
                    'currency': account.get('currency'),
                    'account_status': account.get('account_status'),
                    'amount_spent': float(account.get('amount_spent', 0)) / 100,  # centavos para reais
                    'balance': float(account.get('balance', 0)) / 100,
                    'spend_cap': float(account.get('spend_cap', 0)) / 100 if account.get('spend_cap') else None,
                    'business_name': account.get('business_name'),
                    'business_id': account.get('business', {}).get('id') if account.get('business') else None,
                    'timezone_name': account.get('timezone_name'),
                })
            
            logger.info(f"Obtidas {len(accounts_data)} contas de anúncios")
            return accounts_data
            
        except Exception as e:
            logger.error(f"Erro ao obter contas de anúncios: {e}")
            raise
    
    def get_campaigns(self, account_id: str, status: Optional[List[str]] = None) -> List[Dict]:
        """
        Obtém campanhas de uma conta de anúncios
        
        Args:
            account_id: ID da conta (act_123456)
            status: Lista de status para filtrar (ACTIVE, PAUSED, etc.)
        
        Returns:
            Lista de campanhas
        """
        try:
            if not account_id.startswith('act_'):
                account_id = f'act_{account_id}'
            
            account = AdAccount(account_id)
            
            params = {
                'fields': [
                    'id',
                    'name',
                    'objective',
                    'status',
                    'daily_budget',
                    'lifetime_budget',
                    'start_time',
                    'stop_time',
                    'created_time',
                    'updated_time',
                ]
            }
            
            if status:
                params['filtering'] = [{'field': 'status', 'operator': 'IN', 'value': status}]
            
            campaigns = account.get_campaigns(params=params)
            
            campaigns_data = []
            for campaign in campaigns:
                campaigns_data.append({
                    'campaign_id': campaign.get('id'),
                    'name': campaign.get('name'),
                    'objective': campaign.get('objective'),
                    'status': campaign.get('status'),
                    'daily_budget': float(campaign.get('daily_budget', 0)) / 100 if campaign.get('daily_budget') else None,
                    'lifetime_budget': float(campaign.get('lifetime_budget', 0)) / 100 if campaign.get('lifetime_budget') else None,
                    'start_time': campaign.get('start_time'),
                    'stop_time': campaign.get('stop_time'),
                    'created_time': campaign.get('created_time'),
                    'updated_time': campaign.get('updated_time'),
                })
            
            logger.info(f"Obtidas {len(campaigns_data)} campanhas para conta {account_id}")
            return campaigns_data
            
        except Exception as e:
            logger.error(f"Erro ao obter campanhas: {e}")
            raise
    
    def get_campaign_insights(
        self,
        campaign_id: str,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
        breakdown: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Obtém insights/métricas de uma campanha
        
        Args:
            campaign_id: ID da campanha
            date_start: Data inicial (padrão: 30 dias atrás)
            date_end: Data final (padrão: hoje)
            breakdown: Breakdowns (ex: ['age', 'gender', 'placement'])
        
        Returns:
            Lista de insights
        """
        try:
            if not date_start:
                date_start = datetime.now() - timedelta(days=settings.DEFAULT_DATA_RANGE)
            if not date_end:
                date_end = datetime.now()
            
            campaign = Campaign(campaign_id)
            
            params = {
                'time_range': {
                    'since': date_start.strftime('%Y-%m-%d'),
                    'until': date_end.strftime('%Y-%m-%d')
                },
                'fields': [
                    'impressions',
                    'clicks',
                    'spend',
                    'reach',
                    'frequency',
                    'cpc',
                    'cpm',
                    'ctr',
                    'cpp',
                    'actions',
                    'conversions',
                    'conversion_values',
                    'cost_per_action_type',
                    'inline_link_clicks',
                    'unique_inline_link_clicks',
                    'video_30_sec_watched_actions',
                    'video_p25_watched_actions',
                    'video_p50_watched_actions',
                    'video_p75_watched_actions',
                    'video_p100_watched_actions',
                ],
                'level': 'campaign',
                'time_increment': 1,  # Dados diários
            }
            
            if breakdown:
                params['breakdowns'] = breakdown
            
            insights = campaign.get_insights(params=params)
            
            insights_data = []
            for insight in insights:
                insight_dict = {
                    'date': insight.get('date_start'),
                    'impressions': int(insight.get('impressions', 0)),
                    'clicks': int(insight.get('clicks', 0)),
                    'spend': float(insight.get('spend', 0)),
                    'reach': int(insight.get('reach', 0)),
                    'frequency': float(insight.get('frequency', 0)),
                    'cpc': float(insight.get('cpc', 0)),
                    'cpm': float(insight.get('cpm', 0)),
                    'ctr': float(insight.get('ctr', 0)),
                    'link_clicks': int(insight.get('inline_link_clicks', 0)),
                    'unique_link_clicks': int(insight.get('unique_inline_link_clicks', 0)),
                }
                
                # Processar ações/conversões
                actions = insight.get('actions', [])
                for action in actions:
                    action_type = action.get('action_type')
                    value = int(action.get('value', 0))
                    
                    if action_type == 'post_engagement':
                        insight_dict['post_engagement'] = value
                    elif action_type == 'post_reaction':
                        insight_dict['post_reactions'] = value
                    elif action_type == 'comment':
                        insight_dict['post_comments'] = value
                    elif action_type == 'post':
                        insight_dict['post_shares'] = value
                    elif action_type == 'lead':
                        insight_dict['leads'] = value
                    elif action_type == 'purchase':
                        insight_dict['purchases'] = value
                
                # Processar valores de conversão
                conversion_values = insight.get('conversion_values', [])
                for conv_value in conversion_values:
                    if conv_value.get('action_type') == 'purchase':
                        insight_dict['purchase_value'] = float(conv_value.get('value', 0))
                
                # Calcular métricas
                if insight_dict['clicks'] > 0:
                    insight_dict['conversions'] = insight_dict.get('leads', 0) + insight_dict.get('purchases', 0)
                    if insight_dict['conversions'] > 0:
                        insight_dict['cpa'] = insight_dict['spend'] / insight_dict['conversions']
                
                # ROAS
                if insight_dict.get('purchase_value', 0) > 0 and insight_dict['spend'] > 0:
                    insight_dict['roas'] = insight_dict['purchase_value'] / insight_dict['spend']
                
                # Breakdown data
                if breakdown:
                    for key in breakdown:
                        insight_dict[key] = insight.get(key)
                
                insights_data.append(insight_dict)
            
            logger.info(f"Obtidos {len(insights_data)} insights para campanha {campaign_id}")
            return insights_data
            
        except Exception as e:
            logger.error(f"Erro ao obter insights da campanha: {e}")
            raise
    
    def get_adsets(self, campaign_id: str) -> List[Dict]:
        """
        Obtém conjuntos de anúncios de uma campanha
        
        Args:
            campaign_id: ID da campanha
        
        Returns:
            Lista de ad sets
        """
        try:
            campaign = Campaign(campaign_id)
            
            adsets = campaign.get_ad_sets(fields=[
                'id',
                'name',
                'status',
                'daily_budget',
                'lifetime_budget',
                'optimization_goal',
                'billing_event',
                'bid_amount',
                'targeting',
                'start_time',
                'end_time',
                'created_time',
                'updated_time',
            ])
            
            adsets_data = []
            for adset in adsets:
                adsets_data.append({
                    'adset_id': adset.get('id'),
                    'name': adset.get('name'),
                    'status': adset.get('status'),
                    'daily_budget': float(adset.get('daily_budget', 0)) / 100 if adset.get('daily_budget') else None,
                    'lifetime_budget': float(adset.get('lifetime_budget', 0)) / 100 if adset.get('lifetime_budget') else None,
                    'optimization_goal': adset.get('optimization_goal'),
                    'billing_event': adset.get('billing_event'),
                    'bid_amount': float(adset.get('bid_amount', 0)) / 100 if adset.get('bid_amount') else None,
                    'targeting': adset.get('targeting'),
                    'start_time': adset.get('start_time'),
                    'end_time': adset.get('end_time'),
                })
            
            logger.info(f"Obtidos {len(adsets_data)} ad sets para campanha {campaign_id}")
            return adsets_data
            
        except Exception as e:
            logger.error(f"Erro ao obter ad sets: {e}")
            raise
    
    def get_ads(self, adset_id: str) -> List[Dict]:
        """
        Obtém anúncios de um conjunto de anúncios
        
        Args:
            adset_id: ID do ad set
        
        Returns:
            Lista de anúncios
        """
        try:
            adset = AdSet(adset_id)
            
            ads = adset.get_ads(fields=[
                'id',
                'name',
                'status',
                'creative',
                'preview_shareable_link',
            ])
            
            ads_data = []
            for ad in ads:
                creative = ad.get('creative', {})
                
                ads_data.append({
                    'ad_id': ad.get('id'),
                    'name': ad.get('name'),
                    'status': ad.get('status'),
                    'creative': creative,
                    'preview_url': ad.get('preview_shareable_link'),
                })
            
            logger.info(f"Obtidos {len(ads_data)} anúncios para ad set {adset_id}")
            return ads_data
            
        except Exception as e:
            logger.error(f"Erro ao obter anúncios: {e}")
            raise


# Instância global do serviço
meta_ads_service = MetaAdsService()
