"""
Router: Contas de Anúncios
Gerencia contas de anúncios da Meta
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime

from app.database import get_db
from app.models.ad_account import AdAccount
from app.services.meta_api import MetaAdsService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def list_ad_accounts(db: Session = Depends(get_db)):
    """
    Lista todas as contas de anúncios
    Sincroniza com a Meta API se necessário
    """
    try:
        # Buscar do banco
        accounts = db.query(AdAccount).all()
        
        # Se não há contas, buscar da API
        if not accounts:
            logger.info("Nenhuma conta no banco, sincronizando com Meta...")
            service = MetaAdsService()
            accounts_data = service.get_ad_accounts()
            
            # Salvar no banco
            for acc_data in accounts_data:
                account = AdAccount(
                    user_id=1,  # TODO: Usar usuário autenticado
                    account_id=acc_data['account_id'],
                    name=acc_data['name'],
                    currency=acc_data['currency'],
                    account_status=acc_data['account_status'],
                    amount_spent=acc_data['amount_spent'],
                    balance=acc_data['balance'],
                    spend_cap=acc_data['spend_cap'],
                    business_name=acc_data['business_name'],
                    business_id=acc_data['business_id'],
                    timezone_name=acc_data['timezone_name'],
                    last_synced_at=datetime.now()
                )
                db.add(account)
            
            db.commit()
            db.refresh(accounts)
            accounts = db.query(AdAccount).all()
        
        return {
            "count": len(accounts),
            "accounts": [
                {
                    "id": acc.id,
                    "account_id": acc.account_id,
                    "name": acc.name,
                    "currency": acc.currency,
                    "amount_spent": acc.amount_spent,
                    "balance": acc.balance,
                    "business_name": acc.business_name,
                    "last_synced_at": acc.last_synced_at
                }
                for acc in accounts
            ]
        }
    
    except Exception as e:
        logger.error(f"Erro ao listar contas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_ad_accounts(db: Session = Depends(get_db)):
    """
    Força sincronização das contas com a Meta API
    """
    try:
        service = MetaAdsService()
        accounts_data = service.get_ad_accounts()
        
        synced_count = 0
        for acc_data in accounts_data:
            # Verificar se já existe
            account = db.query(AdAccount).filter(
                AdAccount.account_id == acc_data['account_id']
            ).first()
            
            if account:
                # Atualizar
                account.name = acc_data['name']
                account.amount_spent = acc_data['amount_spent']
                account.balance = acc_data['balance']
                account.account_status = acc_data['account_status']
                account.last_synced_at = datetime.now()
            else:
                # Criar
                account = AdAccount(
                    user_id=1,  # TODO: Usar usuário autenticado
                    **acc_data,
                    last_synced_at=datetime.now()
                )
                db.add(account)
            
            synced_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "synced_count": synced_count,
            "message": f"Sincronizadas {synced_count} contas de anúncios"
        }
    
    except Exception as e:
        logger.error(f"Erro ao sincronizar contas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}")
async def get_ad_account(account_id: str, db: Session = Depends(get_db)):
    """
    Obtém detalhes de uma conta específica
    """
    account = db.query(AdAccount).filter(
        AdAccount.account_id == account_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    return {
        "id": account.id,
        "account_id": account.account_id,
        "name": account.name,
        "currency": account.currency,
        "amount_spent": account.amount_spent,
        "balance": account.balance,
        "spend_cap": account.spend_cap,
        "business_name": account.business_name,
        "timezone_name": account.timezone_name,
        "campaigns_count": len(account.campaigns),
        "last_synced_at": account.last_synced_at
    }
