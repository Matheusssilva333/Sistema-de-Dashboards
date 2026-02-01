# 🔑 Como Obter Credenciais da Meta Ads API

## Passo a Passo Completo

### 1️⃣ Criar Conta Facebook Business Manager

1. Acesse: https://business.facebook.com
2. Clique em "Criar conta"
3. Preencha os dados da sua empresa
4. Confirme o e-mail
5. Configure métodos de pagamento (se necessário)

---

### 2️⃣ Criar App no Facebook Developers

1. **Acessar Developer Console**
   - URL: https://developers.facebook.com/apps/
   - Faça login com sua conta Facebook

2. **Criar Novo App**
   - Clique em "Criar App"
   - Selecione tipo: **"Business"**
   - Nome do App: "Traffic Dashboard" (ou seu nome)
   - E-mail de contato
   - Clique em "Criar App"

3. **Anotar Credenciais Básicas**
   - Vá em: **Configurações → Básico**
   - Copie:
     - ✅ **ID do App** (META_APP_ID)
     - ✅ **Chave Secreta do App** (META_APP_SECRET)

---

### 3️⃣ Adicionar Produto "Marketing API"

1. **No Dashboard do App**
   - Procure por "Marketing API"
   - Clique em "Configurar" ou "Adicionar"

2. **Configurar Permissões**
   - Vá em: **Ferramentas → API Marketing → Ferramentas**
   - Selecione as permissões necessárias:
     - ✅ `ads_read`
     - ✅ `ads_management`
     - ✅ `business_management`
     - ✅ `pages_read_engagement` (opcional)

---

### 4️⃣ Configurar OAuth Redirect URI

1. **Adicionar Plataforma**
   - Configurações → Básico
   - Role até "Adicionar plataforma"
   - Selecione "Site"

2. **Configurar URLs**
   - **URL do site**: `http://localhost:8000`
   - **Domínios do aplicativo**: `localhost`

3. **URIs de redirecionamento OAuth válidos**
   - Vá em: **Produtos → Facebook Login → Configurações**
   - Adicione: `http://localhost:8000/auth/callback`
   - Salve alterações

---

### 5️⃣ Obter Token de Acesso

#### Opção A: Graph API Explorer (Desenvolvimento/Teste)

1. **Acessar Explorer**
   - URL: https://developers.facebook.com/tools/explorer/

2. **Configurar**
   - Selecione seu App no dropdown
   - Versão da API: **v18.0** (ou mais recente)

3. **Gerar Token**
   - Clique em "Generate Access Token"
   - Faça login se solicitado
   - Aceite as permissões:
     - ✅ ads_read
     - ✅ ads_management
     - ✅ business_management

4. **Copiar Token**
   - Copie o token gerado
   - Cole no arquivo `.env` como `META_ACCESS_TOKEN`

⚠️ **Importante**: 
- Tokens do Explorer expiram em 1-2 horas
- Para produção, use OAuth 2.0 (Opção B)

#### Opção B: OAuth 2.0 Flow (Produção)

1. **Implementado no Sistema**
   - Endpoint: `/auth/login`
   - Callback: `/auth/callback`

2. **Processo**
   - Usuário acessa: `http://localhost:8000/auth/login`
   - Sistema redireciona para Facebook
   - Usuário autoriza o app
   - Facebook retorna código
   - Sistema troca código por token
   - Token salvo automaticamente no banco

#### Opção C: Token de Longa Duração (60 dias)

1. **Com Token de Curta Duração**
   ```bash
   curl -G \
     -d "grant_type=fb_exchange_token" \
     -d "client_id={APP_ID}" \
     -d "client_secret={APP_SECRET}" \
     -d "fb_exchange_token={SHORT_LIVED_TOKEN}" \
     https://graph.facebook.com/v18.0/oauth/access_token
   ```

2. **Resposta**
   ```json
   {
     "access_token": "LONG_LIVED_TOKEN",
     "token_type": "bearer",
     "expires_in": 5184000
   }
   ```

3. **Usar Long-Lived Token**
   - Cole no `.env` como `META_ACCESS_TOKEN`
   - Dura ~60 dias

---

### 6️⃣ Vincular Conta de Anúncios ao App

1. **Business Manager**
   - Acesse: https://business.facebook.com
   - Vá em: **Configurações do Negócio**

2. **Contas de Anúncios**
   - Menu lateral: **Contas de anúncios**
   - Selecione sua conta
   - Clique em "Atribuir pessoas" ou "Atribuir parceiros"

3. **Adicionar App**
   - Selecione seu app criado
   - Conceda permissões de:
     - ✅ Analisar
     - ✅ Anunciar
     - Salve

---

### 7️⃣ Testar Configuração

1. **Verificar Token**
   ```bash
   curl -G \
     -d "access_token={SEU_TOKEN}" \
     https://graph.facebook.com/v18.0/me/adaccounts
   ```

2. **Resposta Esperada**
   ```json
   {
     "data": [
       {
         "id": "act_123456789",
         "account_id": "123456789",
         "name": "Minha Conta de Anúncios"
       }
     ]
   }
   ```

3. **Se funcionar**
   - ✅ Token válido
   - ✅ Permissões corretas
   - ✅ Conta vinculada

---

### 8️⃣ Configurar Arquivo .env

```env
# Meta Ads API
META_APP_ID=123456789012345
META_APP_SECRET=abc123def456ghi789jkl012mno345pq
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
META_API_VERSION=v18.0
```

---

## 🔍 Troubleshooting

### Erro: "Invalid OAuth access token"

**Causas:**
- Token expirado
- Token sem permissões
- App não vinculado à conta

**Solução:**
1. Gere novo token no Graph API Explorer
2. Verifique permissões (ads_read, ads_management)
3. Vincule app à conta de anúncios no Business Manager

---

### Erro: "(#200) The user hasn't authorized the application to perform this action"

**Causa:** Falta de permissões

**Solução:**
1. Graph API Explorer
2. Clique em "Get Token" → "Get User Access Token"
3. Selecione todas as permissões de ads
4. Gere novo token

---

### Erro: "Application does not have permission for this request"

**Causa:** App não tem acesso à conta de anúncios

**Solução:**
1. Business Manager → Contas de anúncios
2. Selecione a conta
3. Adicione seu app
4. Conceda permissão de "Anunciar"

---

### Token Expira Rapidamente

**Problema:** Tokens do Explorer duram 1-2 horas

**Solução:**
- Use token de longa duração (60 dias) - Opção C
- Ou implemente OAuth completo (refresh automático)

---

## 📋 Checklist de Configuração

Antes de usar o sistema, verifique:

- [ ] Conta no Business Manager criada
- [ ] App criado no Developers
- [ ] Marketing API adicionada ao app
- [ ] Permissões configuradas (ads_read, ads_management)
- [ ] OAuth redirect URI configurado
- [ ] Token de acesso gerado
- [ ] Conta de anúncios vinculada ao app
- [ ] Token testado (curl ou Graph API Explorer)
- [ ] .env configurado com credenciais
- [ ] Sistema testado (`/api/ad-accounts/`)

---

## 📚 Links Úteis

### Documentação Oficial
- [Marketing API Guide](https://developers.facebook.com/docs/marketing-apis)
- [Access Tokens Guide](https://developers.facebook.com/docs/facebook-login/guides/access-tokens)
- [Permissions Reference](https://developers.facebook.com/docs/permissions/reference)

### Ferramentas
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
- [Business Manager](https://business.facebook.com)
- [Apps Dashboard](https://developers.facebook.com/apps/)

### Suporte
- [Stack Overflow - Facebook API](https://stackoverflow.com/questions/tagged/facebook-graph-api)
- [Meta Developer Community](https://developers.facebook.com/community/)

---

## 🎯 Próximos Passos

Após obter as credenciais:

1. ✅ Cole no arquivo `.env`
2. ✅ Execute `python scripts/init_db.py`
3. ✅ Execute `python scripts/sync_data.py`
4. ✅ Inicie o servidor: `uvicorn app.main:app --reload`
5. ✅ Acesse: http://localhost:8000

---

**🎉 Pronto! Agora você pode usar o Traffic Dashboard com suas campanhas Meta!**
