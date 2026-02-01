# 🏗️ Arquitetura do Sistema

## Visão Geral

O **Traffic Dashboard** é um sistema full-stack para gestão de tráfego pago da Meta (Facebook/Instagram Ads), construído com arquitetura moderna e escalável.

## 🎯 Componentes Principais

### 1. Backend (FastAPI)

```
app/
├── main.py              # Entry point da aplicação
├── config.py            # Configurações centralizadas
├── database.py          # SQLAlchemy setup
├── models/              # Models do banco de dados
│   ├── user.py         # Usuários
│   ├── ad_account.py   # Contas de anúncios
│   ├── campaign.py     # Campanhas
│   ├── ad_set.py       # Conjuntos de anúncios
│   ├── ad.py           # Anúncios
│   └── insight.py      # Métricas diárias
├── routers/             # API Endpoints
│   ├── auth.py         # Autenticação
│   ├── ad_accounts.py  # Contas
│   ├── campaigns.py    # Campanhas
│   ├── insights.py     # Insights
│   └── reports.py      # Relatórios
└── services/            # Lógica de negócio
    └── meta_api.py     # Integração Meta Ads API
```

**Tecnologias:**
- FastAPI: Framework web assíncrono
- SQLAlchemy: ORM
- Pydantic: Validação de dados
- Facebook Business SDK: Cliente oficial Meta

### 2. Frontend (HTML/CSS/JS)

```
frontend/
├── templates/
│   └── index.html       # SPA principal
└── static/
    ├── css/
    │   └── main.css    # Estilos premium
    └── js/
        └── app.js      # Lógica Alpine.js
```

**Tecnologias:**
- Alpine.js: Reatividade leve
- Chart.js: Gráficos interativos
- Vanilla CSS: Design system premium

### 3. Banco de Dados

**SQLite** (desenvolvimento) / **PostgreSQL** (produção)

**Schema Principal:**

```sql
users
├── id (PK)
├── email
├── meta_access_token
└── meta_token_expires_at

ad_accounts
├── id (PK)
├── user_id (FK)
├── account_id (Meta ID)
├── name
├── currency
└── amount_spent

campaigns
├── id (PK)
├── ad_account_id (FK)
├── campaign_id (Meta ID)
├── name
├── objective
├── status
├── daily_budget
├── impressions (cache)
├── clicks (cache)
├── spend (cache)
└── ctr, cpc, cpm (calculados)

ad_sets
├── id (PK)
├── campaign_id (FK)
├── adset_id (Meta ID)
├── name
├── targeting (JSON)
└── optimization_goal

ads
├── id (PK)
├── adset_id (FK)
├── ad_id (Meta ID)
├── name
└── creative (JSON)

insights
├── id (PK)
├── campaign_id (FK)
├── date
├── impressions
├── clicks
├── spend
├── conversions
├── ctr, cpc, cpm, roas (calculados)
└── placement, device
```

### 4. Cache (Redis)

- Cache de respostas da API
- Sessões de usuário
- Rate limiting
- Broker para Celery

### 5. Worker (Celery)

**Tasks:**
- Sincronização automática periódica
- Processamento de relatórios
- Envio de alertas
- Agregação de métricas

## 🔄 Fluxo de Dados

### 1. Autenticação OAuth

```
Usuário → Facebook OAuth → Callback → Token armazenado → API habilitada
```

### 2. Sincronização de Dados

```
Celery Beat (agendador)
    ↓
Celery Worker
    ↓
MetaAdsService.get_ad_accounts()
    ↓
Facebook Marketing API
    ↓
Dados salvos no PostgreSQL
    ↓
Cache atualizado no Redis
```

### 3. Consulta de Dashboards

```
Frontend (Alpine.js)
    ↓
API Request (/api/insights/summary)
    ↓
FastAPI Router (insights.py)
    ↓
Verifica Redis Cache
    ├─ Cache hit → Retorna dados
    └─ Cache miss ↓
       SQLAlchemy Query
           ↓
       Calcula métricas
           ↓
       Armazena no Redis
           ↓
       Retorna JSON
```

### 4. Exportação de Relatórios

```
Usuário clica "Exportar"
    ↓
API Request (/api/reports/export/excel)
    ↓
Query insights do banco
    ↓
Pandas DataFrame
    ↓
Excel gerado (openpyxl)
    ↓
Download do arquivo
```

## 🔐 Segurança

### Autenticação
- OAuth 2.0 com Facebook
- JWT tokens para sessões
- Refresh token automático

### Dados Sensíveis
- Variáveis de ambiente (.env)
- Secrets no Docker
- Tokens criptografados no banco

### API Security
- Rate limiting (Redis)
- CORS configurado
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy)

## 📊 Métricas e KPIs

### Métricas Básicas (da API)
- Impressões
- Cliques
- Gasto
- Alcance
- Frequência

### Métricas Calculadas
- CTR = (Cliques / Impressões) × 100
- CPC = Gasto / Cliques
- CPM = (Gasto / Impressões) × 1000
- CPA = Gasto / Conversões
- ROAS = Valor Conversões / Gasto

### Agregações
- Por dia (insights table)
- Por campanha (campaigns table cache)
- Por período (query com GROUP BY)
- Por objetivo/placement/device (insights breakdowns)

## 🚀 Deploy

### Desenvolvimento
```bash
uvicorn app.main:app --reload
```

### Produção (Docker)
```yaml
services:
  - web (FastAPI + Uvicorn)
  - db (PostgreSQL)
  - redis (Cache)
  - celery_worker (Tasks)
  - celery_beat (Scheduler)
  - flower (Monitoring)
  - nginx (Reverse Proxy)
```

### Escalabilidade
- **Horizontal**: Múltiplas instâncias do web server (Nginx load balancer)
- **Vertical**: Aumentar recursos de containers
- **Cache**: Redis para reduzir queries ao banco
- **CDN**: Servir assets estáticos

## 📈 Performance

### Otimizações
1. **Índices no Banco**: campaign_id, date, account_id
2. **Cache Redis**: Respostas de API, métricas agregadas
3. **Lazy Loading**: Dados carregados sob demanda
4. **Pagination**: Limite de resultados por página
5. **Async I/O**: FastAPI assíncrono

### Benchmarks Esperados
- Tempo de resposta API: < 200ms
- Sincronização de conta: ~2-5s
- Geração de relatório: ~1-3s
- Dashboard load: < 1s

## 🔄 Sincronização

### Estratégias

**1. Pull (Implementado)**
- Usuário clica "Sincronizar"
- API busca dados sob demanda
- Atualiza banco e cache

**2. Scheduled (Celery Beat)**
```python
@celery.task
def sync_all_accounts():
    for account in AdAccount.query.all():
        sync_account_data(account.id)
```

**3. Webhook (Futuro)**
- Meta envia notificações de mudanças
- Sincronização em tempo real

## 🎨 Design System

### Tema Dark Premium
- Background: #0f172a (navy)
- Cards: #1e293b (slate)
- Primary: #3b82f6 (blue)
- Secondary: #8b5cf6 (purple)
- Success: #10b981 (green)
- Warning: #f59e0b (amber)
- Danger: #ef4444 (red)

### Componentes
- KPI Cards com gradientes
- Gráficos Chart.js
- Tabelas responsivas
- Badges de status
- Loading states
- Toast notifications

## 📦 Dependências Principais

**Backend:**
- fastapi==0.109.0
- facebook-business==19.0.0
- sqlalchemy==2.0.25
- redis==5.0.1
- celery==5.3.6
- pandas==2.1.4

**Frontend:**
- alpine.js@3.13.3
- chart.js@4.4.1
- font-awesome@6.4.0

## 🔮 Roadmap Futuro

### Fase 2
- [ ] Alertas automáticos (e-mail/SMS)
- [ ] Comparação de períodos
- [ ] Análise de audiência avançada
- [ ] Recommendations ML

### Fase 3
- [ ] Integração Google Ads
- [ ] Integração TikTok Ads
- [ ] Multi-tenant (white-label)
- [ ] Mobile app (React Native)

### Fase 4
- [ ] IA para otimização de campanhas
- [ ] Predição de performance
- [ ] A/B testing automático
- [ ] Budget optimization

---

**Última atualização:** Janeiro 2026
