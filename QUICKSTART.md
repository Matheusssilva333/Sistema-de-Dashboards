# ============================================
# GUIA DE INÍCIO RÁPIDO
# ============================================

## 📋 Pré-requisitos

1. Python 3.11+ instalado
2. Conta Facebook Business Manager
3. App criado no Facebook Developers
4. Token de acesso da Meta Ads API

## 🚀 Instalação Rápida

### Passo 1: Clonar e Configurar

```bash
# Navegar para o diretório
cd "Sistema de Dashboard"

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate
```

### Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

### Passo 3: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
copy .env.example .env

# Editar .env com suas credenciais
notepad .env
```

**Variáveis Obrigatórias:**
- `META_APP_ID`: ID do seu app no Facebook
- `META_APP_SECRET`: Secret do app
- `META_ACCESS_TOKEN`: Token de acesso (obtido no Graph API Explorer)

### Passo 4: Inicializar Banco de Dados

```bash
python scripts/init_db.py
```

### Passo 5: Sincronizar Dados (Opcional)

```bash
python scripts/sync_data.py
```

### Passo 6: Iniciar Servidor

```bash
uvicorn app.main:app --reload
```

📱 **Acesse:** http://localhost:8000

## 🐳 Com Docker (Alternativa)

```bash
# Configurar .env primeiro
copy .env.example .env

# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## 🔑 Obter Token de Acesso Meta

### Método 1: Graph API Explorer (Desenvolvimento)

1. Acesse: https://developers.facebook.com/tools/explorer/
2. Selecione seu app
3. Clique em "Generate Access Token"
4. Selecione as permissões:
   - `ads_read`
   - `ads_management`
   - `business_management`
5. Copie o token gerado

⚠️ **Atenção**: Tokens do Explorer expiram em 1-2 horas. Para produção, use OAuth.

### Método 2: OAuth 2.0 (Produção)

1. Configure o redirect URI no seu app: `http://localhost:8000/auth/callback`
2. Acesse: http://localhost:8000/auth/login
3. Autorize o aplicativo
4. O token será salvo automaticamente

## 📊 Estrutura de Pastas

```
Sistema de Dashboard/
├── app/                    # Código da aplicação
│   ├── models/            # Models SQLAlchemy
│   ├── routers/           # API endpoints
│   ├── services/          # Lógica de negócio
│   ├── config.py          # Configurações
│   ├── database.py        # Setup do banco
│   └── main.py            # Entry point
├── frontend/              # Frontend
│   ├── static/           # CSS, JS, imagens
│   └── templates/        # HTML templates
├── scripts/              # Scripts utilitários
│   ├── init_db.py       # Inicializar BD
│   └── sync_data.py     # Sincronizar dados
├── logs/                 # Logs da aplicação
├── docker-compose.yml    # Docker Compose
├── Dockerfile           # Docker image
├── requirements.txt     # Dependências Python
└── README.md           # Documentação

## 📖 Endpoints da API

### Contas de Anúncios
- `GET /api/ad-accounts/` - Listar contas
- `POST /api/ad-accounts/sync` - Sincronizar contas

### Campanhas
- `GET /api/campaigns/?account_id=act_123` - Listar campanhas
- `GET /api/campaigns/{campaign_id}` - Detalhes da campanha
- `POST /api/campaigns/{campaign_id}/sync` - Sincronizar campanha

### Insights/Métricas
- `GET /api/insights/campaign/{campaign_id}` - Insights da campanha
- `GET /api/insights/summary?days=30` - Resumo geral

### Relatórios
- `GET /api/reports/export/excel?campaign_id=123` - Exportar Excel
- `GET /api/reports/export/csv?campaign_id=123` - Exportar CSV

## 🔧 Desenvolvimento

### Executar Testes

```bash
pytest
```

### Code Quality

```bash
# Formatação
black app/

# Linting
flake8 app/

# Type checking
mypy app/
```

## 🐛 Troubleshooting

### Erro: "Invalid OAuth access token"

- Verifique se o token está correto no `.env`
- Gere um novo token no Graph API Explorer
- Confira se as permissões foram concedidas

### Erro: "No module named 'app'"

- Certifique-se de estar no diretório correto
- Ative o ambiente virtual
- Reinstale as dependências: `pip install -r requirements.txt`

### Banco de dados vazio

- Execute: `python scripts/init_db.py`
- Execute: `python scripts/sync_data.py`

### Porta 8000 já em uso

```bash
# Use outra porta
uvicorn app.main:app --port 8080
```

## 📚 Recursos Úteis

- [Meta Marketing API Docs](https://developers.facebook.com/docs/marketing-apis)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Facebook Business Manager](https://business.facebook.com/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs em `logs/app.log`
2. Consulte a documentação da Meta API
3. Abra uma issue no GitHub

## 🎉 Próximos Passos

1. ✅ Configurar credenciais da Meta
2. ✅ Sincronizar suas contas e campanhas
3. ✅ Explorar os dashboards
4. ⬜ Configurar sincronização automática (Celery)
5. ⬜ Personalizar métricas e alertas
6. ⬜ Deploy em produção

---

**Desenvolvido com ❤️ para Gestores de Tráfego**
