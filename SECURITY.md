# 🛡️ DOCUMENTAÇÃO DE SEGURANÇA
# Sistema de Dashboards com Proteção Avançada

**Versão:** 2.0.0  
**Data:** 2024  
**Classificação:** Segurança Empresarial

---

## 📋 ÍNDICE

1. [Visão Geral de Segurança](#visão-geral)
2. [Arquitetura de Segurança](#arquitetura)
3. [Proteções Implementadas](#proteções)
4. [Configuração de Segurança](#configuração)
5. [Auditoria e Logs](#auditoria)
6. [Resposta a Incidentes](#incidentes)
7. [Checklist de Deployment](#checklist)
8. [Compliance](#compliance)

---

## 🔐 VISÃO GERAL DE SEGURANÇA

### Princípios de Segurança

Este sistema foi desenvolvido seguindo os princípios de:

1. **Defense in Depth (Defesa em Profundidade)**
   - Múltiplas camadas de proteção
   - Nenhum ponto único de falha
   - Redundância em controles críticos

2. **Least Privilege (Menor Privilégio)**
   - Usuários têm apenas permissões necessárias
   - Tokens com escopo limitado
   - Segregação de funções

3. **Zero Trust**
   - Validação contínua de identidade
   - Verificação de todas as requisições
   - Não confia automaticamente em nada

4. **Secure by Default**
   - Configurações seguras por padrão
   - HTTPS obrigatório em produção
   - Logs de segurança sempre ativos

---

## 🏗️ ARQUITETURA DE SEGURANÇA

### Camadas de Proteção

```
┌─────────────────────────────────────────┐
│     CAMADA 1: Network & Infrastructure  │
│  - Firewall                             │
│  - DDoS Protection (Cloudflare)         │
│  - VPN/Private Network                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     CAMADA 2: Application Gateway       │
│  - Rate Limiting (Slowapi)              │
│  - IP Blocking                          │
│  - Request Size Validation              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     CAMADA 3: Application Security      │
│  - CSRF Protection                      │
│  - XSS Prevention                       │
│  - SQL Injection Prevention             │
│  - Input Sanitization                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     CAMADA 4: Authentication & AuthZ    │
│  - JWT Tokens                           │
│  - Password Hashing (bcrypt)            │
│  - API Key Management                   │
│  - Session Management                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     CAMADA 5: Data Security             │
│  - Encryption at Rest (Fernet)          │
│  - Encryption in Transit (TLS 1.3)      │
│  - Secure Key Storage                   │
│  - Database Encryption                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     CAMADA 6: Monitoring & Logging      │
│  - Security Event Logging               │
│  - Anomaly Detection                    │
│  - Audit Trail                          │
│  - Alert System                         │
└─────────────────────────────────────────┘
```

---

## 🛡️ PROTEÇÕES IMPLEMENTADAS

### 1. Rate Limiting - Proteção DDoS

**Biblioteca:** Slowapi  
**Localização:** `app/security.py`

**Limites por Endpoint:**

| Endpoint | Limite | Motivo |
|----------|--------|--------|
| Login | 5/min | Prevenir brute force |
| Dashboard Creation | 10/min | Prevenir abuse |
| Widget Data | 100/min | Permitir refresh frequente |
| Export | 5/min | Operação custosa |
| API geral | 60/min | Tráfego normal |

**Código:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request):
    ...
```

**Ações ao ultrapassar limite:**
1. HTTP 429 Too Many Requests
2. Log de segurança
3. Bloqueio temporário do IP (após 3x 429)

---

### 2. CSRF Protection

**Biblioteca:** itsdangerous  
**Localização:** `app/security.py`

**Funcionamento:**
1. Token gerado ao criar sessão
2. Token incluído em formulários/requisições
3. Validação em operações state-changing (POST/PUT/DELETE)
4. Tokens expiram em 1 hora

**Código:**
```python
from itsdangerous import URLSafeTimedSerializer

class CSRFProtection:
    def __init__(self, secret_key: str):
        self.serializer = URLSafeTimedSerializer(secret_key)
    
    def generate_token(self, session_id: str) -> str:
        return self.serializer.dumps(session_id, salt="csrf-token")
    
    def validate_token(self, token: str, session_id: str) -> bool:
        try:
            data = self.serializer.loads(token, salt="csrf-token", max_age=3600)
            return data == session_id
        except:
            return False
```

---

### 3. SQL Injection Prevention

**Camadas de Proteção:**

1. **ORM (SQLAlchemy)** - Queries parametrizadas
2. **Input Sanitization** - Remove caracteres perigosos
3. **Prepared Statements** - Separação de dados e comandos

**Caracteres Bloqueados:**
- `;` (finalização de comando)
- `--` (comentário SQL)
- `/*` `*/` (comentário em bloco)
- `xp_`, `sp_` (procedimentos system)
- `DROP`, `DELETE`, `INSERT`, `UPDATE` (em inputs de usuário)

**Código:**
```python
@staticmethod
def sanitize_sql(text: str) -> str:
    dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_', 
                      'DROP', 'DELETE', 'INSERT', 'UPDATE']
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    return sanitized
```

---

### 4. XSS Prevention

**Biblioteca:** Bleach  
**Localização:** `app/security.py`

**Proteções:**

1. **Input Sanitization**
   - Remove scripts maliciosos
   - Permite apenas tags seguras
   - Escapa caracteres especiais

2. **Content Security Policy (CSP)**
   ```
   Content-Security-Policy: 
     default-src 'self';
     script-src 'self' 'unsafe-inline' 'unsafe-eval';
     style-src 'self' 'unsafe-inline';
   ```

3. **Output Encoding**
   - HTML entities encoding
   - JSON encoding
   - URL encoding

**Código:**
```python
import bleach

@staticmethod
def sanitize_html(text: str) -> str:
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    return bleach.clean(text, tags=allowed_tags, strip=True)
```

---

### 5. Password Security

**Biblioteca:** bcrypt  
**Localização:** `app/security.py`

**Requisitos de Senha:**
- Mínimo 8 caracteres
- 1+ letra maiúscula
- 1+ letra minúscula
- 1+ número
- 1+ caractere especial
- Não estar na lista de senhas comuns

**Armazenamento:**
- Hash bcrypt (cost factor 12)
- Salt único por senha
- Nunca armazena senha em texto plano

**Código:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

### 6. Data Encryption

**Biblioteca:** Cryptography (Fernet)  
**Localização:** `app/security.py`

**Dados Criptografados:**
- Tokens de acesso de API
- Chaves de integração
- Dados sensíveis de usuário
- Senhas de terceiros

**Características:**
- Symmetric encryption (AES 128)
- Authentication (HMAC)
- Timestamp incluído

**Código:**
```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self):
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        key = base64.urlsafe_b64encode(key[:32])
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()
```

---

### 7. Security Headers

**Localização:** `app/security.py`

**Headers Implementados:**

```python
SECURITY_HEADERS = {
    # Previne MIME sniffing
    "X-Content-Type-Options": "nosniff",
    
    # Previne clickjacking
    "X-Frame-Options": "DENY",
    
    # Ativa proteção XSS do browser
    "X-XSS-Protection": "1; mode=block",
    
    # Força HTTPS
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    
    # Content Security Policy
    "Content-Security-Policy": "default-src 'self'; ...",
    
    # Controla referrer
    "Referrer-Policy": "strict-origin-when-cross-origin",
    
    # Permissões de features
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}
```

---

### 8. IP Blocking System

**Localização:** `app/security.py`

**Funcionamento:**

1. **Contagem de Tentativas Falhas**
   - Rastreamento por IP
   - Limite: 5 tentativas

2. **Bloqueio Automático**
   - Duração: 30 minutos
   - Log de evento
   - Notificação de admin (TODO)

3. **Desbloqueio**
   - Automático após timeout
   - Manual por admin
   - Reset de contador

**Código:**
```python
class IPBlocker:
    def record_failed_attempt(self, ip: str, max_attempts: int = 5):
        self.failed_attempts[ip] = self.failed_attempts.get(ip, 0) + 1
        
        if self.failed_attempts[ip] >= max_attempts:
            self.blocked_ips[ip] = datetime.utcnow() + timedelta(minutes=30)
            security_logger.log_suspicious_activity(
                "IP bloqueado por múltiplas tentativas",
                ip
            )
```

---

### 9. API Key Management

**Localização:** `app/security.py`

**Características:**

1. **Geração Segura**
   - Prefixo: `sk_`
   - 32 bytes aleatórios (secrets.token_urlsafe)
   - Única e não previsível

2. **Armazenamento**
   - Hash da chave (nunca plaintext)
   - Metadata: user_id, created_at, last_used
   - Flag is_active

3. **Validação**
   - Verifica existência
   - Verifica status ativo
   - Atualiza last_used

4. **Revogação**
   - Instant revocation
   - Não pode ser reativada
   - Log de evento

---

### 10. Security Logging

**Localização:** `logs/security.log`  
**Classe:** `SecurityLogger` em `app/security.py`

**Eventos Registrados:**

1. **Autenticação**
   - Login bem-sucedido
   - Login falho
   - Logout
   - Password reset

2. **Autorização**
   - Acesso negado
   - Permissão faltando
   - Escalação de privilégio

3. **Dados**
   - Acesso a dados sensíveis
   - Modificação de dados
   - Exportação de dados
   - Deleção de dados

4. **Segurança**
   - Rate limit excedido
   - IP bloqueado
   - Token CSRF inválido
   - Atividade suspeita

**Formato de Log:**
```
2024-01-01 10:00:00 - SECURITY - LEVEL - MESSAGE
```

**Exemplo:**
```
2024-01-01 10:00:00 - SECURITY - INFO - Login SUCESSO - User: user@example.com, IP: 192.168.1.1
2024-01-01 10:05:00 - SECURITY - WARNING - Login FALHA - User: attacker@evil.com, IP: 10.0.0.1
2024-01-01 10:06:00 - SECURITY - CRITICAL - IP bloqueado - IP: 10.0.0.1, Tentativas: 5
```

---

## ⚙️ CONFIGURAÇÃO DE SEGURANÇA

### Variáveis de Ambiente Críticas

```env
# SECRET KEY - MUST BE STRONG
SECRET_KEY=change-this-to-random-32-char-string-min

# Ambiente
ENVIRONMENT=production
DEBUG=False

# HTTPS
HTTPS_ONLY=True
SSL_REDIRECT=True

# Database
DATABASE_URL=postgresql://user:strongpassword@db:5432/dashboards

# Redis (para rate limiting)
REDIS_URL=redis://:redispassword@redis:6379/0

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_STORAGE_URL=redis://redis:6379/1

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Session
SESSION_TIMEOUT=3600  # 1 hora
```

---

## 📊 AUDITORIA E LOGS

### Tipos de Logs

1. **Application Logs** (`logs/app.log`)
   - Eventos de aplicação
   - Erros e exceções
   - Informações gerais

2. **Security Logs** (`logs/security.log`)
   - Eventos de segurança
   - Tentativas de ataque
   - Violações de política

3. **Access Logs** (Nginx/Uvicorn)
   - Requisições HTTP
   - IPs e user agents
   - Status codes

### Retenção de Logs

- **Produção:** 90 dias
- **Staging:** 30 dias
- **Development:** 7 dias

### Análise de Logs

**Ferramentas Recomendadas:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana + Loki
- Datadog
- Sentry (para erros)

**Alertas Importantes:**
- 5+ logins falhos em 5 minutos
- IP bloqueado
- Acesso a dados sensíveis
- Mudança de permissões
- Export de grandes volumes de dados

---

## 🚨 RESPOSTA A INCIDENTES

### Procedimento em Caso de Ataque

1. **Detecção**
   - Monitoramento de logs
   - Alertas automáticos
   - Relatórios de usuários

2. **Contenção**
   - Bloquear IP atacante
   - Revogar tokens comprometidos
   - Isolar sistema afetado

3. **Investigação**
   - Analisar logs de segurança
   - Identificar vetor de ataque
   - Avaliar impacto

4. **Erradicação**
   - Corrigir vulnerabilidade
   - Aplicar patches
   - Atualizar regras de firewall

5. **Recuperação**
   - Restaurar de backup (se necessário)
   - Validar integridade dos dados
   - Monitorar atividade

6. **Pós-Incidente**
   - Documentar incidente
   - Atualizar procedimentos
   - Treinar equipe

### Contatos de Emergência

```
Security Team: security@dashboards.com
On-Call: +55 (11) 9999-9999
Slack: #security-alerts
```

---

## ✅ CHECKLIST DE DEPLOYMENT

### Antes do Deploy

- [ ] `DEBUG=False` configurado
- [ ] `SECRET_KEY` gerado (min 32 chars)
- [ ] HTTPS/SSL configurado
- [ ] Firewall configurado
- [ ] Database com senha forte
- [ ] Redis com senha
- [ ] Variáveis de ambiente validadas
- [ ] CORS configurado corretamente
- [ ] Rate limiting testado
- [ ] Logs configurados
- [ ] Backup automático configurado
- [ ] Monitoramento ativo

### Após o Deploy

- [ ] Health check respondendo
- [ ] SSL certificate válido
- [ ] Headers de segurança ativos
- [ ] Rate limiting funcionando
- [ ] Logs sendo gerados
- [ ] Alertas configurados
- [ ] Scan de vulnerabilidades executado
- [ ] Penetration test realizado (opcional)

### Testes de Segurança

```bash
# OWASP ZAP scan
zap-cli quick-scan https://yourdomain.com

# SSL test
ssllabs-scan --usecache yourdomain.com

# Headers check
curl -I https://yourdomain.com | grep -i "x-"

# Rate limit test
for i in {1..10}; do curl https://yourdomain.com/api/test; done
```

---

## 📜 COMPLIANCE

### OWASP Top 10 (2021)

| # | Vulnerabilidade | Status | Proteção |
|---|----------------|--------|----------|
| A01 | Broken Access Control | ✅ | JWT, RBAC |
| A02 | Cryptographic Failures | ✅ | Fernet, bcrypt |
| A03 | Injection | ✅ | Sanitização, ORM |
| A04 | Insecure Design | ✅ | Secure by default |
| A05 | Security Misconfiguration | ✅ | Security headers |
| A06 | Vulnerable Components | ✅ | Dependabot |
| A07 | Auth & Session Mgmt | ✅ | JWT, sessions |
| A08 | Software & Data Integrity | ✅ | Checksums |
| A09 | Logging & Monitoring | ✅ | Security logs |
| A10 | SSRF | ✅ | Input validation |

### LGPD (Lei Geral de Proteção de Dados)

- ✅ Consentimento explícito
- ✅ Criptografia de dados pessoais
- ✅ Direito ao esquecimento
- ✅ Portabilidade de dados
- ✅ Log de acesso a dados
- ✅ Notificação de incidentes

### GDPR Compliance

- ✅ Data encryption
- ✅ Right to erasure
- ✅ Data portability
- ✅ Breach notification
- ✅ Privacy by design

---

## 📚 REFERÊNCIAS

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

**Última Atualização:** 2024  
**Responsável:** Security Team  
**Revisão:** Anual ou após incidentes
