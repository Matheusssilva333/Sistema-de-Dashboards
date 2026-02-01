# 🛡️ Sistema de Geração de Dashboards para Gestão de Trafego

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Security](https://img.shields.io/badge/security-enterprise-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)

Sistema empresarial completo de geração de dashboards dinâmicos com múltiplas camadas de segurança avançada para gestores de trafego.

---

## 🎯 **Solução Especializada para Gestores de Tráfego**

Este sistema foi desenhado especificamente para atender às necessidades de agências e gestores de tráfego profissionais:

### 🚀 **Para o Gestor de Tráfego**
- **Integração Nativa Meta Ads**: Conexão direta com a API para dados em tempo real.
- **Métricas Cruciais**: Acesso imediato a ROAS, CPA, CTR, CPM, CPC e Conversões.
- **Dashboards Automatizados**: Chega de planilhas manuais. Gere relatórios em segundos.
- **Multi-Conta**: Gerencie múltiplos clientes em um único painel.
- **Segurança de Dados**: Proteção total dos dados dos seus clientes.

### 📊 **Visualizações Profissionais**
- **Funil de Vendas Completo**: Do alcance até a conversão.
- **Análise Demográfica**: Saiba exatamente quem está comprando (Idade, Gênero, Região).
- **Comparativo de Resultados**: Análise de performance vs investimento.
- **Relatórios White-Label**: Exporte PDFs profissionais para enviar aos clientes.

---

### 📊 **Geração de Dashboards**
- ✅ **Criação Dinâmica** - Crie dashboards personalizados com drag-and-drop
- ✅ **Templates Predefinidos** - Templates focados em performance (Marketing, Vendas)
- ✅ **Widgets Customizáveis** - 10+ tipos de gráficos e visualizações
- ✅ **Multi-Fonte de Dados** - Integração profunda com Meta Ads
- ✅ **Insights Automáticos** - Cálculo automático de ROAS e CPA
- ✅ **Compartilhamento** - Compartilhe dashboards com sua equipe de gestão
- ✅ **Exportação** - Exporte em PDF, Excel para apresentar resultados


## 🚀 **Instalação e Configuração**

### **Pré-requisitos*
- Python 3.11+
- PostgreSQL ou SQLite
- Redis (opcional, mas recomendado)
- Docker (opcional)

### **Instalação Local**

```bash
# Clone o repositório
git clone https://github.com/Matheusssilva333/Sistema-de-Dashboards.git
cd Sistema-de-Dashboards

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# Inicialize o banco de dados
python scripts/init_db.py

# Execute o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Instalação com Docker**

```bash
# Clone o repositório
git clone https://github.com/Matheusssilva333/Sistema-de-Dashboards.git
cd Sistema-de-Dashboards

# Configure variáveis de ambiente
cp .env.example .env

# Inicie com Docker Compose
docker-compose up -d

# Acesse em http://localhost:8000
```

---

## 📖 **Uso da API**

### **Endpoints de Dashboards**

#### **Listar Templates**
```bash
GET /api/dashboards/templates
Rate Limit: 20/min

Response:
[
  {
    "name": "Visão Geral de Marketing",
    "description": "Dashboard completo para análise de campanhas",
    "category": "Marketing"
  }
]
```

#### **Criar Dashboard**
```bash
POST /api/dashboards
Rate Limit: 10/min
Security: Input sanitization, CSRF protection

Body:
{
  "name": "Meu Dashboard",
  "description": "Dashboard personalizado",
  "owner_id": "user123",
  "widgets": [...]
}
```

#### **Obter Dados de Widget**
```bash
GET /api/dashboards/{dashboard_id}/widgets/{widget_id}/data
Rate Limit: 100/min

Response:
{
  "widget_id": "widget123",
  "data": {
    "labels": ["Jan", "Feb", "Mar"],
    "datasets": [...]
  },
  "last_updated": "2024-01-01T00:00:00"
}
```

#### **Compartilhar Dashboard**
```bash
POST /api/dashboards/{dashboard_id}/share
Rate Limit: 10/min
Security: Permission validation

Body:
{
  "user_ids": ["user1", "user2"]
}
```

### **Rate Limits por Endpoint**

| Endpoint | Limite | Descrição |
|----------|--------|-----------|
| `/api/dashboards/templates` | 20/min | Listagem de templates |
| `/api/dashboards` (POST) | 10/min | Criação de dashboards |
| `/api/dashboards/{id}` (GET) | 60/min | Visualização |
| `/api/dashboards/{id}` (PUT) | 15/min | Atualização |
| `/api/dashboards/{id}/widgets` | 20/min | Gestão de widgets |
| `/api/dashboards/{id}/export` | 5/min | Exportação |
| Widget data | 100/min | Dados em tempo real |

---

## 🛡️ **Configuração de Segurança**

### **Variáveis de Ambiente (.env)**

```env
# Application
APP_NAME=Sistema de Dashboards
DEBUG=False  # SEMPRE False em produção
SECRET_KEY=sua-chave-secreta-super-forte-aqui-min-32-chars
ENVIRONMENT=production

# Security
HTTPS_ONLY=True
CSRF_PROTECTION=True
RATE_LIMIT_ENABLED=True

# Database (use PostgreSQL em produção)
DATABASE_URL=postgresql://user:password@localhost:5432/dashboards

# Redis (para rate limiting)
REDIS_URL=redis://localhost:6379/0

# Meta Ads API
META_APP_ID=seu_app_id
META_APP_SECRET=seu_app_secret
META_ACCESS_TOKEN=seu_token

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### **Checklist de Segurança para Produção**

- [ ] `DEBUG=False` no .env
- [ ] `SECRET_KEY` forte e única (min 32 caracteres)
- [ ] HTTPS configurado (Let's Encrypt)
- [ ] Firewall configurado (apenas portas necessárias)
- [ ] PostgreSQL com senha forte
- [ ] Redis com senha configurada
- [ ] Backup automático configurado
- [ ] Monitoramento de logs ativo
- [ ] Rate limiting ativado
- [ ] CORS configurado corretamente
- [ ] Certificados SSL válidos
- [ ] Senhas de banco de dados rotacionadas
- [ ] Scan de vulnerabilidades realizado

---

## 📊 **Templates de Dashboard**

### **1. Visão Geral de Marketing**
- Investimento Total
- Conversões
- ROAS
- CTR
- Tendência de Investimento
- Conversões por Campanha
- Tabela de Performance

### **2. Dashboard de Vendas**
- Receita Total
- Total de Pedidos
- Ticket Médio
- Tendência de Receita

### **3. Dashboard Financeiro**
- ROI
- Lucro
- Custo por Resultado

### **4. Dashboard de Performance**
- Impressões
- Cliques
- CTR
- CPC
- Mapa de Performance

---

## 🎨 **Tipos de Widgets Disponíveis**

| Widget | Descrição | Uso Ideal |
|--------|-----------|-----------|
| **Metric** | Número único com variação | KPIs principais |
| **Line** | Gráfico de linha | Tendências temporais |
| **Bar** | Gráfico de barras | Comparações |
| **Pie** | Gráfico de pizza | Distribuições |
| **Donut** | Gráfico rosquinha | Proporções |
| **Area** | Gráfico de área | Volumes |
| **Gauge** | Medidor | Percentuais |
| **Heatmap** | Mapa de calor | Correlações |
| **Table** | Tabela de dados | Dados detalhados |
| **Scatter** | Dispersão | Relações |

---

## 📁 **Estrutura do Projeto**

```
Sistema-de-Dashboards/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Entry point com segurança
│   ├── config.py                    # Configurações
│   ├── database.py                  # Conexão DB
│   ├── security.py                  # 🔐 Módulo de segurança
│   ├── dashboard_generator.py       # 📊 Gerador de dashboards
│   ├── models/                      # SQLAlchemy models
│   ├── routers/
│   │   ├── auth.py                 # Autenticação
│   │   ├── dashboards.py           # 📊 API de dashboards
│   │   ├── campaigns.py            # Campanhas
│   │   ├── insights.py             # Insights
│   │   └── reports.py              # Relatórios
│   └── services/
│       ├── meta_api.py             # Integração Meta Ads
│       └── analytics.py            # Processamento
├── frontend/
│   ├── static/                      # CSS, JS, Images
│   └── templates/                   # HTML templates
├── logs/
│   ├── app.log                      # Logs gerais
│   └── security.log                 # 🔐 Logs de segurança
├── scripts/
│   └── init_db.py                   # Inicialização
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔒 **Logs de Segurança**

O sistema mantém logs detalhados de eventos de segurança em `logs/security.log`:

```
2024-01-01 10:00:00 - SECURITY - INFO - Login SUCESSO - User: user@example.com, IP: 192.168.1.1
2024-01-01 10:05:00 - SECURITY - WARNING - Login FALHA - User: attacker@evil.com, IP: 10.0.0.1
2024-01-01 10:06:00 - SECURITY - WARNING - IP bloqueado por múltiplas tentativas - IP: 10.0.0.1
2024-01-01 10:10:00 - SECURITY - INFO - Acesso a dados - User: user123, Resource: dashboard:dash_abc, Action: create
```

---

## 🧪 **Testes**

```bash
# Execute todos os testes
pytest

# Testes com cobertura
pytest --cov=app --cov-report=html

# Testes de segurança
pytest tests/security/

# Lint e formatação
black app/
flake8 app/
mypy app/
```

---

## 📈 **Monitoramento**

### **Health Check**
```bash
GET /health

Response:
{
  "status": "healthy",
  "app_name": "Sistema de Geração de Dashboards",
  "version": "2.0.0",
  "environment": "production"
}
```

### **Métricas Disponíveis**
- Taxa de requisições
- Tempo de resposta
- Erros 4xx/5xx
- Rate limits ativados
- IPs bloqueados
- Tentativas de login falhas

---

## 🤝 **Contribuindo**

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📝 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🆘 **Suporte**

- **Issues**: [GitHub Issues](https://github.com/Matheusssilva333/Sistema-de-Dashboards/issues)
- **Documentação**: `/docs` (quando em modo debug)
- **Email**: suporte@dashboards.com

---

## 🎯 **Roadmap**

### **Versão 2.1**
- [ ] Autenticação 2FA
- [ ] Webhooks para alertas
- [ ] IA para detecção de anomalias
- [ ] Dashboard mobile app

### **Versão 3.0**
- [ ] Integração com mais plataformas
- [ ] Machine Learning para predições
- [ ] White-label para agências
- [ ] Multi-idioma

---

## 🏆 **Certificações de Segurança**

- ✅ OWASP Top 10 Protection
- ✅ SQL Injection Prevention
- ✅ XSS Protection
- ✅ CSRF Protection
- ✅ DDoS Mitigation
- ✅ Secure Password Storage
- ✅ Rate Limiting
- ✅ Security Headers
- ✅ Input Validation
- ✅ Audit Logging

---

**Desenvolvido com ❤️ e 🔐 por Matheus Silva**

*Sistema de Dashboard Empresarial - Versão 2.0.0*
