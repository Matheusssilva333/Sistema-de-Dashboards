"""
Router: Autenticação
Gerencia login, OAuth com Facebook, e tokens
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.services.meta_api import MetaAdsService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/login")
async def login_redirect():
    """
    Redireciona para o fluxo de OAuth do Facebook
    """
    # TODO: Implementar fluxo OAuth completo
    # Por enquanto, retorna instruções
    return {
        "message": "Implemente o fluxo OAuth do Facebook",
        "instructions": [
            "1. Configure o App no Facebook Developers",
            "2. Obtenha um token de acesso",
            "3. Configure no arquivo .env",
            "4. O token pode ser obtido em: https://developers.facebook.com/tools/explorer/"
        ]
    }


@router.get("/callback")
async def oauth_callback(code: str, db: Session = Depends(get_db)):
    """
    Callback do OAuth - recebe o código e troca por token
    """
    # TODO: Implementar troca de código por token
    pass


@router.get("/status")
async def auth_status():
    """
    Verifica status da autenticação com Meta
    """
    try:
        service = MetaAdsService()
        # Tenta obter contas para validar token
        accounts = service.get_ad_accounts()
        return {
            "authenticated": True,
            "accounts_count": len(accounts)
        }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e)
        }
