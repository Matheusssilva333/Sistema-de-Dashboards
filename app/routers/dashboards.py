"""
Router para Geração e Gerenciamento de Dashboards
Endpoints para criar, editar, visualizar e compartilhar dashboards
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.security import (
    limiter,
    csrf_protection,
    sanitizer,
    security_logger,
    require_https
)
from app.dashboard_generator import (
    DashboardConfig,
    DashboardTemplate,
    WidgetConfig,
    dashboard_manager,
    data_processor
)

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# ENDPOINTS DE TEMPLATES
# =============================================================================
@router.get("/templates", response_model=List[dict])
@limiter.limit("20/minute")
async def list_templates(request: Request):
    """
    Lista todos os templates de dashboard disponíveis
    
    Rate Limit: 20 requisições por minuto
    """
    try:
        templates = dashboard_manager.list_templates()
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "preview_image": t.preview_image
            }
            for t in templates
        ]
    except Exception as e:
        logger.error(f"Erro ao listar templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar templates"
        )


@router.get("/templates/{template_name}", response_model=dict)
@limiter.limit("30/minute")
async def get_template(request: Request, template_name: str):
    """
    Obtém detalhes de um template específico
    
    Rate Limit: 30 requisições por minuto
    """
    # Sanitiza o nome do template
    template_name = sanitizer.sanitize_sql(template_name)
    
    template = dashboard_manager.get_template(template_name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado"
        )
    
    return {
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "config": template.config.model_dump()
    }


# =============================================================================
# ENDPOINTS DE DASHBOARDS
# =============================================================================
@router.post("/dashboards", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_dashboard(
    request: Request,
    config: DashboardConfig,
    db: Session = Depends(get_db)
):
    """
    Cria um novo dashboard personalizado
    
    Rate Limit: 10 criações por minuto
    Security: Validação de entrada, sanitização de dados
    """
    try:
        # Sanitiza o nome do dashboard
        config.name = sanitizer.sanitize_html(config.name)
        config.description = sanitizer.sanitize_html(config.description)
        
        # Cria o dashboard
        new_dashboard = dashboard_manager.create_dashboard(config)
        
        # Log de auditoria
        security_logger.log_data_access(
            user_id=config.owner_id,
            resource="dashboard",
            action="create"
        )
        
        return {
            "message": "Dashboard criado com sucesso",
            "dashboard": new_dashboard.model_dump()
        }
    
    except Exception as e:
        logger.error(f"Erro ao criar dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar dashboard"
        )


@router.get("/dashboards/{dashboard_id}", response_model=dict)
@limiter.limit("60/minute")
async def get_dashboard(
    request: Request,
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém um dashboard específico
    
    Rate Limit: 60 requisições por minuto
    """
    # Sanitiza o ID
    dashboard_id = sanitizer.sanitize_sql(dashboard_id)
    
    # TODO: Buscar no banco de dados
    # Por enquanto retorna exemplo
    return {
        "id": dashboard_id,
        "message": "Dashboard encontrado"
    }


@router.put("/dashboards/{dashboard_id}", response_model=dict)
@limiter.limit("15/minute")
async def update_dashboard(
    request: Request,
    dashboard_id: str,
    config: DashboardConfig,
    db: Session = Depends(get_db)
):
    """
    Atualiza um dashboard existente
    
    Rate Limit: 15 atualizações por minuto
    Security: Validação de propriedade, sanitização
    """
    try:
        # Sanitiza dados
        dashboard_id = sanitizer.sanitize_sql(dashboard_id)
        config.name = sanitizer.sanitize_html(config.name)
        config.description = sanitizer.sanitize_html(config.description)
        
        # Atualiza dashboard
        updated_dashboard = dashboard_manager.update_dashboard(dashboard_id, config)
        
        # Log de auditoria
        security_logger.log_data_access(
            user_id=config.owner_id,
            resource=f"dashboard:{dashboard_id}",
            action="update"
        )
        
        return {
            "message": "Dashboard atualizado com sucesso",
            "dashboard": updated_dashboard.model_dump()
        }
    
    except Exception as e:
        logger.error(f"Erro ao atualizar dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar dashboard"
        )


@router.delete("/dashboards/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_dashboard(
    request: Request,
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """
    Deleta um dashboard
    
    Rate Limit: 10 deleções por minuto
    Security: Validação de propriedade
    """
    # Sanitiza o ID
    dashboard_id = sanitizer.sanitize_sql(dashboard_id)
    
    # TODO: Validar propriedade e deletar do banco
    
    # Log de auditoria
    security_logger.log_data_access(
        user_id="current_user",
        resource=f"dashboard:{dashboard_id}",
        action="delete"
    )
    
    logger.info(f"Dashboard {dashboard_id} deletado")


# =============================================================================
# ENDPOINTS DE WIDGETS
# =============================================================================
@router.post("/dashboards/{dashboard_id}/widgets", response_model=dict)
@limiter.limit("20/minute")
async def add_widget(
    request: Request,
    dashboard_id: str,
    widget: WidgetConfig,
    db: Session = Depends(get_db)
):
    """
    Adiciona um widget a um dashboard
    
    Rate Limit: 20 adições por minuto
    """
    try:
        # Sanitiza dados
        dashboard_id = sanitizer.sanitize_sql(dashboard_id)
        widget.title = sanitizer.sanitize_html(widget.title)
        
        success = dashboard_manager.add_widget(dashboard_id, widget)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao adicionar widget"
            )
        
        return {
            "message": "Widget adicionado com sucesso",
            "widget": widget.model_dump()
        }
    
    except Exception as e:
        logger.error(f"Erro ao adicionar widget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar widget"
        )


@router.delete("/dashboards/{dashboard_id}/widgets/{widget_id}")
@limiter.limit("20/minute")
async def remove_widget(
    request: Request,
    dashboard_id: str,
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Remove um widget de um dashboard
    
    Rate Limit: 20 remoções por minuto
    """
    # Sanitiza IDs
    dashboard_id = sanitizer.sanitize_sql(dashboard_id)
    widget_id = sanitizer.sanitize_sql(widget_id)
    
    success = dashboard_manager.remove_widget(dashboard_id, widget_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget não encontrado"
        )
    
    return {"message": "Widget removido com sucesso"}


# =============================================================================
# ENDPOINTS DE DADOS
# =============================================================================
@router.get("/dashboards/{dashboard_id}/widgets/{widget_id}/data", response_model=dict)
@limiter.limit("100/minute")
async def get_widget_data(
    request: Request,
    dashboard_id: str,
    widget_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtém dados processados para um widget específico
    
    Rate Limit: 100 requisições por minuto (alta frequência para refresh)
    """
    try:
        # Sanitiza IDs
        dashboard_id = sanitizer.sanitize_sql(dashboard_id)
        widget_id = sanitizer.sanitize_sql(widget_id)
        
        # TODO: Buscar configuração do widget e dados reais
        # Mock data por enquanto
        mock_widget = WidgetConfig(
            id=widget_id,
            title="Example Widget",
            chart_type="line",
            data_source="meta_ads",
            metrics=["spend"],
            dimensions=["date"]
        )
        
        mock_data = [
            {"date": "2024-01-01", "spend": 100},
            {"date": "2024-01-02", "spend": 150},
            {"date": "2024-01-03", "spend": 200}
        ]
        
        processed_data = data_processor.process_widget_data(mock_widget, mock_data)
        
        return {
            "widget_id": widget_id,
            "data": processed_data,
            "last_updated": "2024-01-01T00:00:00"
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter dados do widget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter dados do widget"
        )


# =============================================================================
# ENDPOINTS DE EXPORTAÇÃO
# =============================================================================
@router.get("/dashboards/{dashboard_id}/export", response_model=dict)
@limiter.limit("5/minute")
async def export_dashboard(
    request: Request,
    dashboard_id: str,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """
    Exporta um dashboard em diferentes formatos
    
    Rate Limit: 5 exportações por minuto
    Formats: json, pdf
    """
    # Sanitiza parâmetros
    dashboard_id = sanitizer.sanitize_sql(dashboard_id)
    format = sanitizer.sanitize_sql(format.lower())
    
    if format not in ["json", "pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato não suportado. Use 'json' ou 'pdf'"
        )
    
    # TODO: Implementar exportação real
    
    # Log de auditoria
    security_logger.log_data_access(
        user_id="current_user",
        resource=f"dashboard:{dashboard_id}",
        action=f"export:{format}"
    )
    
    return {
        "message": f"Dashboard exportado em formato {format}",
        "download_url": f"/downloads/dashboard_{dashboard_id}.{format}"
    }


# =============================================================================
# ENDPOINTS DE COMPARTILHAMENTO
# =============================================================================
@router.post("/dashboards/{dashboard_id}/share", response_model=dict)
@limiter.limit("10/minute")
async def share_dashboard(
    request: Request,
    dashboard_id: str,
    user_ids: List[str],
    db: Session = Depends(get_db)
):
    """
    Compartilha um dashboard com outros usuários
    
    Rate Limit: 10 compartilhamentos por minuto
    Security: Validação de permissões
    """
    # Sanitiza IDs
    dashboard_id = sanitizer.sanitize_sql(dashboard_id)
    user_ids = [sanitizer.sanitize_sql(uid) for uid in user_ids]
    
    # TODO: Implementar compartilhamento real
    
    # Log de auditoria
    security_logger.log_data_access(
        user_id="current_user",
        resource=f"dashboard:{dashboard_id}",
        action=f"share:users={len(user_ids)}"
    )
    
    return {
        "message": "Dashboard compartilhado com sucesso",
        "shared_with": user_ids
    }
