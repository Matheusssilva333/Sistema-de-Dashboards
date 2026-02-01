"""
Sistema de Geração de Dashboards Dinâmicos
Permite criar, customizar e gerenciar dashboards personalizados
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS E TIPOS
# =============================================================================
class ChartType(str, Enum):
    """Tipos de gráficos disponíveis"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DONUT = "donut"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    METRIC = "metric"


class DataSource(str, Enum):
    """Fontes de dados disponíveis"""
    META_ADS = "meta_ads"
    GOOGLE_ADS = "google_ads"
    ANALYTICS = "analytics"
    CUSTOM_API = "custom_api"
    DATABASE = "database"
    CSV_FILE = "csv_file"


class AggregationType(str, Enum):
    """Tipos de agregação de dados"""
    SUM = "sum"
    AVG = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"


class TimeRange(str, Enum):
    """Períodos de tempo predefinidos"""
    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_YEAR = "this_year"
    CUSTOM = "custom"


# =============================================================================
# SCHEMAS
# =============================================================================
class WidgetConfig(BaseModel):
    """Configuração de um widget no dashboard"""
    id: str
    title: str
    chart_type: ChartType
    data_source: DataSource
    metrics: List[str]
    dimensions: List[str] = []
    aggregation: AggregationType = AggregationType.SUM
    filters: Dict[str, Any] = {}
    time_range: TimeRange = TimeRange.LAST_30_DAYS
    custom_start_date: Optional[str] = None
    custom_end_date: Optional[str] = None
    refresh_interval: int = 300  # segundos
    position: Dict[str, int] = {"x": 0, "y": 0, "w": 4, "h": 3}
    options: Dict[str, Any] = {}
    
    @validator('custom_start_date', 'custom_end_date')
    def validate_dates(cls, v):
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Data deve estar no formato YYYY-MM-DD')
        return v


class DashboardConfig(BaseModel):
    """Configuração completa de um dashboard"""
    id: Optional[str] = None
    name: str
    description: str = ""
    widgets: List[WidgetConfig] = []
    layout: str = "grid"  # grid, flex, custom
    is_public: bool = False
    owner_id: str
    shared_with: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    theme: str = "light"  # light, dark, custom
    tags: List[str] = []


class DashboardTemplate(BaseModel):
    """Template de dashboard predefinido"""
    name: str
    description: str
    category: str
    preview_image: Optional[str] = None
    config: DashboardConfig


# =============================================================================
# GERENCIADOR DE DASHBOARDS
# =============================================================================
class DashboardManager:
    """Gerenciador de criação e manipulação de dashboards"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, DashboardTemplate]:
        """Carrega templates predefinidos"""
        return {
            "marketing_overview": DashboardTemplate(
                name="Visão Geral de Marketing",
                description="Dashboard completo para análise de campanhas de marketing",
                category="Marketing",
                config=self._create_marketing_template()
            ),
            "sales_dashboard": DashboardTemplate(
                name="Dashboard de Vendas",
                description="Análise completa de vendas e conversões",
                category="Vendas",
                config=self._create_sales_template()
            ),
            "financial_dashboard": DashboardTemplate(
                name="Dashboard Financeiro",
                description="Métricas financeiras e ROI",
                category="Financeiro",
                config=self._create_financial_template()
            ),
            "performance_dashboard": DashboardTemplate(
                name="Dashboard de Performance",
                description="KPIs de performance de campanhas",
                category="Performance",
                config=self._create_performance_template()
            )
        }
    
    def _create_marketing_template(self) -> DashboardConfig:
        """Cria template de dashboard de marketing"""
        return DashboardConfig(
            name="Visão Geral de Marketing",
            description="Dashboard completo para análise de campanhas",
            owner_id="system",
            widgets=[
                WidgetConfig(
                    id="total_spend",
                    title="Investimento Total",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["spend"],
                    aggregation=AggregationType.SUM,
                    position={"x": 0, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="total_conversions",
                    title="Conversões",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["conversions"],
                    aggregation=AggregationType.SUM,
                    position={"x": 3, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="roas",
                    title="ROAS",
                    chart_type=ChartType.GAUGE,
                    data_source=DataSource.META_ADS,
                    metrics=["purchase_roas"],
                    aggregation=AggregationType.AVG,
                    position={"x": 6, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="ctr",
                    title="CTR",
                    chart_type=ChartType.GAUGE,
                    data_source=DataSource.META_ADS,
                    metrics=["ctr"],
                    aggregation=AggregationType.AVG,
                    position={"x": 9, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="spend_trend",
                    title="Tendência de Investimento",
                    chart_type=ChartType.LINE,
                    data_source=DataSource.META_ADS,
                    metrics=["spend"],
                    dimensions=["date"],
                    time_range=TimeRange.LAST_30_DAYS,
                    position={"x": 0, "y": 2, "w": 6, "h": 4}
                ),
                WidgetConfig(
                    id="conversions_by_campaign",
                    title="Conversões por Campanha",
                    chart_type=ChartType.BAR,
                    data_source=DataSource.META_ADS,
                    metrics=["conversions"],
                    dimensions=["campaign_name"],
                    aggregation=AggregationType.SUM,
                    position={"x": 6, "y": 2, "w": 6, "h": 4}
                ),
                WidgetConfig(
                    id="performance_metrics",
                    title="Métricas de Performance",
                    chart_type=ChartType.TABLE,
                    data_source=DataSource.META_ADS,
                    metrics=["impressions", "clicks", "ctr", "cpc", "spend"],
                    dimensions=["campaign_name"],
                    position={"x": 0, "y": 6, "w": 12, "h": 4}
                )
            ],
            layout="grid",
            theme="light"
        )
    
    def _create_sales_template(self) -> DashboardConfig:
        """Cria template de dashboard de vendas"""
        return DashboardConfig(
            name="Dashboard de Vendas",
            description="Análise completa de vendas",
            owner_id="system",
            widgets=[
                WidgetConfig(
                    id="total_revenue",
                    title="Receita Total",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["purchase_value"],
                    aggregation=AggregationType.SUM,
                    position={"x": 0, "y": 0, "w": 4, "h": 2}
                ),
                WidgetConfig(
                    id="total_orders",
                    title="Total de Pedidos",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["purchases"],
                    aggregation=AggregationType.SUM,
                    position={"x": 4, "y": 0, "w": 4, "h": 2}
                ),
                WidgetConfig(
                    id="avg_order_value",
                    title="Ticket Médio",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["purchase_value"],
                    aggregation=AggregationType.AVG,
                    position={"x": 8, "y": 0, "w": 4, "h": 2}
                ),
                WidgetConfig(
                    id="revenue_trend",
                    title="Tendência de Receita",
                    chart_type=ChartType.AREA,
                    data_source=DataSource.META_ADS,
                    metrics=["purchase_value"],
                    dimensions=["date"],
                    position={"x": 0, "y": 2, "w": 12, "h": 4}
                )
            ],
            layout="grid",
            theme="light"
        )
    
    def _create_financial_template(self) -> DashboardConfig:
        """Cria template de dashboard financeiro"""
        return DashboardConfig(
            name="Dashboard Financeiro",
            description="Análise financeira e ROI",
            owner_id="system",
            widgets=[
                WidgetConfig(
                    id="roi",
                    title="ROI",
                    chart_type=ChartType.GAUGE,
                    data_source=DataSource.META_ADS,
                    metrics=["purchase_roas"],
                    aggregation=AggregationType.AVG,
                    position={"x": 0, "y": 0, "w": 6, "h": 3}
                ),
                WidgetConfig(
                    id="profit",
                    title="Lucro",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["purchase_value", "spend"],
                    aggregation=AggregationType.SUM,
                    position={"x": 6, "y": 0, "w": 6, "h": 3}
                ),
                WidgetConfig(
                    id="cost_per_result",
                    title="Custo por Resultado",
                    chart_type=ChartType.LINE,
                    data_source=DataSource.META_ADS,
                    metrics=["cost_per_result"],
                    dimensions=["date"],
                    position={"x": 0, "y": 3, "w": 12, "h": 4}
                )
            ],
            layout="grid",
            theme="light"
        )
    
    def _create_performance_template(self) -> DashboardConfig:
        """Cria template de dashboard de performance"""
        return DashboardConfig(
            name="Dashboard de Performance",
            description="KPIs de performance",
            owner_id="system",
            widgets=[
                WidgetConfig(
                    id="impressions",
                    title="Impressões",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["impressions"],
                    aggregation=AggregationType.SUM,
                    position={"x": 0, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="clicks",
                    title="Cliques",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["clicks"],
                    aggregation=AggregationType.SUM,
                    position={"x": 3, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="ctr_gauge",
                    title="CTR",
                    chart_type=ChartType.GAUGE,
                    data_source=DataSource.META_ADS,
                    metrics=["ctr"],
                    aggregation=AggregationType.AVG,
                    position={"x": 6, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="cpc",
                    title="CPC",
                    chart_type=ChartType.METRIC,
                    data_source=DataSource.META_ADS,
                    metrics=["cpc"],
                    aggregation=AggregationType.AVG,
                    position={"x": 9, "y": 0, "w": 3, "h": 2}
                ),
                WidgetConfig(
                    id="performance_heatmap",
                    title="Mapa de Performance",
                    chart_type=ChartType.HEATMAP,
                    data_source=DataSource.META_ADS,
                    metrics=["ctr", "conversions"],
                    dimensions=["campaign_name", "date"],
                    position={"x": 0, "y": 2, "w": 12, "h": 5}
                )
            ],
            layout="grid",
            theme="light"
        )
    
    def create_dashboard(self, config: DashboardConfig) -> DashboardConfig:
        """Cria um novo dashboard"""
        config.id = self._generate_dashboard_id()
        config.created_at = datetime.utcnow()
        config.updated_at = datetime.utcnow()
        
        logger.info(f"Dashboard criado: {config.name} (ID: {config.id})")
        return config
    
    def update_dashboard(self, dashboard_id: str, config: DashboardConfig) -> DashboardConfig:
        """Atualiza um dashboard existente"""
        config.id = dashboard_id
        config.updated_at = datetime.utcnow()
        
        logger.info(f"Dashboard atualizado: {config.name} (ID: {dashboard_id})")
        return config
    
    def add_widget(self, dashboard_id: str, widget: WidgetConfig) -> bool:
        """Adiciona um widget a um dashboard"""
        logger.info(f"Widget adicionado ao dashboard {dashboard_id}: {widget.title}")
        return True
    
    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove um widget de um dashboard"""
        logger.info(f"Widget {widget_id} removido do dashboard {dashboard_id}")
        return True
    
    def get_template(self, template_name: str) -> Optional[DashboardTemplate]:
        """Retorna um template de dashboard"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[DashboardTemplate]:
        """Lista todos os templates disponíveis"""
        return list(self.templates.values())
    
    def _generate_dashboard_id(self) -> str:
        """Gera um ID único para dashboard"""
        import uuid
        return f"dash_{uuid.uuid4().hex[:12]}"
    
    def export_dashboard(self, config: DashboardConfig) -> str:
        """Exporta configuração do dashboard para JSON"""
        return config.model_dump_json(indent=2)
    
    def import_dashboard(self, json_str: str) -> DashboardConfig:
        """Importa configuração do dashboard de JSON"""
        data = json.loads(json_str)
        return DashboardConfig(**data)


# =============================================================================
# PROCESSADOR DE DADOS
# =============================================================================
class DataProcessor:
    """Processa dados para os widgets do dashboard"""
    
    @staticmethod
    def process_widget_data(
        widget: WidgetConfig,
        raw_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Processa dados para um widget específico"""
        
        if not raw_data:
            return {"labels": [], "datasets": [], "value": 0}
        
        df = pd.DataFrame(raw_data)
        
        # Aplica filtros
        if widget.filters:
            for key, value in widget.filters.items():
                if key in df.columns:
                    df = df[df[key] == value]
        
        # Processa baseado no tipo de gráfico
        if widget.chart_type == ChartType.METRIC:
            return DataProcessor._process_metric(df, widget)
        elif widget.chart_type == ChartType.LINE:
            return DataProcessor._process_line(df, widget)
        elif widget.chart_type == ChartType.BAR:
            return DataProcessor._process_bar(df, widget)
        elif widget.chart_type == ChartType.PIE:
            return DataProcessor._process_pie(df, widget)
        elif widget.chart_type == ChartType.TABLE:
            return DataProcessor._process_table(df, widget)
        elif widget.chart_type == ChartType.GAUGE:
            return DataProcessor._process_gauge(df, widget)
        else:
            return {"error": "Tipo de gráfico não suportado"}
    
    @staticmethod
    def _process_metric(df: pd.DataFrame, widget: WidgetConfig) -> Dict[str, Any]:
        """Processa dados para widget de métrica"""
        metric = widget.metrics[0]
        if metric not in df.columns:
            return {"value": 0, "change": 0}
        
        agg_func = widget.aggregation.value
        value = getattr(df[metric], agg_func)()
        
        return {
            "value": float(value),
            "change": 0,  # TODO: calcular mudança em relação ao período anterior
            "metric": metric,
            "format": "number"
        }
    
    @staticmethod
    def _process_line(df: pd.DataFrame, widget: WidgetConfig) -> Dict[str, Any]:
        """Processa dados para gráfico de linha"""
        if not widget.dimensions:
            return {"labels": [], "datasets": []}
        
        dimension = widget.dimensions[0]
        datasets = []
        
        for metric in widget.metrics:
            if metric in df.columns and dimension in df.columns:
                grouped = df.groupby(dimension)[metric].agg(widget.aggregation.value)
                datasets.append({
                    "label": metric,
                    "data": grouped.tolist(),
                })
        
        labels = df[dimension].unique().tolist() if dimension in df.columns else []
        
        return {
            "labels": labels,
            "datasets": datasets
        }
    
    @staticmethod
    def _process_bar(df: pd.DataFrame, widget: WidgetConfig) -> Dict[str, Any]:
        """Processa dados para gráfico de barras"""
        return DataProcessor._process_line(df, widget)  # Mesma estrutura
    
    @staticmethod
    def _process_pie(df: pd.DataFrame, widget: WidgetConfig) -> Dict[str, Any]:
        """Processa dados para gráfico de pizza"""
        if not widget.dimensions or not widget.metrics:
            return {"labels": [], "data": []}
        
        dimension = widget.dimensions[0]
        metric = widget.metrics[0]
        
        if dimension not in df.columns or metric not in df.columns:
            return {"labels": [], "data": []}
        
        grouped = df.groupby(dimension)[metric].agg(widget.aggregation.value)
        
        return {
            "labels": grouped.index.tolist(),
            "data": grouped.tolist()
        }
    
    @staticmethod
    def _process_table(df: pd.DataFrame, widget: WidgetConfig) -> Dict[str, Any]:
        """Processa dados para tabela"""
        columns = widget.dimensions + widget.metrics
        
        if widget.dimensions:
            # Agrupa por dimensões
            agg_dict = {metric: widget.aggregation.value for metric in widget.metrics}
            df_grouped = df.groupby(widget.dimensions).agg(agg_dict).reset_index()
            df_result = df_grouped[columns] if all(c in df_grouped.columns for c in columns) else df_grouped
        else:
            df_result = df[columns] if all(c in df.columns for c in columns) else df
        
        return {
            "columns": df_result.columns.tolist(),
            "rows": df_result.values.tolist()
        }
    
    @staticmethod
    def _process_gauge(df: pd.DataFrame, widget: WidgetConfig) -> Dict[str, Any]:
        """Processa dados para gráfico gauge"""
        metric_data = DataProcessor._process_metric(df, widget)
        
        return {
            "value": metric_data["value"],
            "min": 0,
            "max": 100,  # TODO: calcular max baseado nos dados
            "metric": metric_data["metric"]
        }


# Instância global do gerenciador
dashboard_manager = DashboardManager()
data_processor = DataProcessor()
