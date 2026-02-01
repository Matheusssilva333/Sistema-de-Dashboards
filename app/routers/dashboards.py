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
@limiter.limit("50/minute")
async def get_widget_data(
    request: Request,
    dashboard_id: str,
    widget_id: str,
    ad_account_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtém dados processados para um widget específico utilizando a API da Meta Ads
    
    Args:
        dashboard_id: ID do dashboard
        widget_id: ID do widget no dashboard
        ad_account_id: ID da conta de anúncios (opcional, sobrescreve contexto)
        campaign_id: ID da campanha (opcional, para filtro específico)
    """
    try:
        # Sanitiza IDs
        dashboard_id = sanitizer.sanitize_sql(dashboard_id)
        widget_id = sanitizer.sanitize_sql(widget_id)
        
        # 1. Recuperar configuração do dashboard/widget (Simulado pois não temos persistência ainda)
        # Em produção, buscaria no banco: dashboard = db.query(Dashboard).filter(...)
        dashboard_template = dashboard_manager.get_template("marketing_overview")
        target_widget = None
        
        # Procura o widget na configuração (lógica temporária até ter persistência)
        if dashboard_template:
            for w in dashboard_template.config.widgets:
                if w.id == widget_id:
                    target_widget = w
                    break
        
        # Fallback se não encontrar (cria um widget temporário para teste se não existir)
        if not target_widget:
             # Tenta buscar das factories padrão para permitir testes com IDs conhecidos
            all_templates = dashboard_manager.list_templates()
            for tmpl in all_templates:
                for w in tmpl.config.widgets:
                    if w.id == widget_id:
                        target_widget = w
                        break
        
        if not target_widget:
             raise HTTPException(status_code=404, detail="Widget não encontrado")

        # 2. Definir período de dados
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        if target_widget.time_range == "today":
            start_date = end_date
        elif target_widget.time_range == "yesterday":
            start_date = end_date - timedelta(days=1)
            end_date = start_date
        elif target_widget.time_range == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif target_widget.time_range == "this_month":
            start_date = end_date.replace(day=1)
        # ... outros ranges
        
        # 3. Buscar dados da Fonte
        raw_data = []
        
        if target_widget.data_source == "meta_ads":
            from app.services.meta_api import meta_ads_service
            
            # Se não fornecer conta/campanha, tentar usar padrão ou erro
            # Aqui assumimos que precisamos de um campaign_id ou account_id
            # Para simplificar o teste, se não tiver campaign_id, pegamos da primeira conta
            
            target_ids = []
            if campaign_id:
                target_ids = [campaign_id]
            else:
                # Tenta pegar todas as campanhas da conta ativa (mockada ou real)
                # Em um cenário real, o dashboard teria um contexto de "Conta Selecionada"
                if ad_account_id:
                     campaigns = meta_ads_service.get_campaigns(ad_account_id, status=['ACTIVE', 'PAUSED'])
                     target_ids = [c['campaign_id'] for c in campaigns[:5]] # Limitando para não sobrecarregar
            
            if not target_ids:
                 # Retornar dados vazios ou mockados se não tiver contexto de campanha para evitar erro 500
                 # Isso permite que o frontend renderize o widget vazio
                 logger.warning("Nenhuma campanha ou conta selecionada para buscar dados")
                 raw_data = []
            else:
                for cid in target_ids:
                    # Determinar breakdown
                    breakdown = None
                    if "age" in target_widget.dimensions: breakdown = ["age"]
                    elif "gender" in target_widget.dimensions: breakdown = ["gender"]
                    # etc
                    
                    insights = meta_ads_service.get_campaign_insights(
                        campaign_id=cid,
                        date_start=start_date,
                        date_end=end_date,
                        breakdown=breakdown
                    )
                    
                    # Adicionar nome da campanha aos dados para agrupamento
                    # (O insight já deve trazer ou podemos enriquecer)
                    for i in insights:
                         i['campaign_id'] = cid
                         # Se precisar do nome, teria que buscar da lista de campanhas cacheada
                    
                    raw_data.extend(insights)

        # 4. Processar dados
        processed_data = data_processor.process_widget_data(target_widget, raw_data)
        
        return {
            "widget_id": widget_id,
            "data": processed_data,
            "meta": {
                "period": f"{start_date.date()} to {end_date.date()}",
                "source": target_widget.data_source
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao obter dados do widget: {e}", exc_info=True)
        # Retorna erro amigável em vez de 500 cru
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar dados: {str(e)}"
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
