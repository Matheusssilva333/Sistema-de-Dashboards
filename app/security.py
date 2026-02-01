"""
Sistema de Segurança Avançado
Implementa múltiplas camadas de proteção contra ataques
"""
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

import bleach
from cryptography.fernet import Fernet
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# RATE LIMITING - Proteção contra DDoS e ataques de força bruta
# =============================================================================
limiter = Limiter(key_func=get_remote_address)


async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler para quando o rate limit é excedido"""
    client_ip = get_remote_address(request)
    security_logger = SecurityLogger()
    security_logger.log_rate_limit_exceeded(client_ip, str(request.url.path))
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "detail": "Muitas requisições. Por favor, aguarde antes de tentar novamente."
        }
    )


# =============================================================================
# CSRF PROTECTION - Proteção contra Cross-Site Request Forgery
# =============================================================================
class CSRFProtection:
    """Gerenciador de tokens CSRF"""
    
    def __init__(self, secret_key: str):
        self.serializer = URLSafeTimedSerializer(secret_key)
    
    def generate_token(self, session_id: str) -> str:
        """Gera um token CSRF único para a sessão"""
        return self.serializer.dumps(session_id, salt="csrf-token")
    
    def validate_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Valida um token CSRF"""
        try:
            data = self.serializer.loads(token, salt="csrf-token", max_age=max_age)
            return data == session_id
        except (BadSignature, SignatureExpired) as e:
            logger.warning(f"Token CSRF inválido: {e}")
            return False


csrf_protection = CSRFProtection(settings.SECRET_KEY)


# =============================================================================
# CRIPTOGRAFIA - Proteção de dados sensíveis
# =============================================================================
class DataEncryption:
    """Gerenciador de criptografia de dados"""
    
    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            # Gera uma chave a partir do SECRET_KEY
            key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
            key = key[:32]  # Fernet precisa de 32 bytes
            import base64
            key = base64.urlsafe_b64encode(key)
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Criptografa dados sensíveis"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Descriptografa dados"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


encryption = DataEncryption()


# =============================================================================
# INPUT SANITIZATION - Proteção contra XSS e injeção de código
# =============================================================================
class InputSanitizer:
    """Sanitizador de inputs para prevenir XSS"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove tags HTML perigosas e scripts"""
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        return bleach.clean(text, tags=allowed_tags, strip=True)
    
    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Remove caracteres perigosos para SQL (adicional ao ORM)"""
        # Remove caracteres especiais SQL
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_', 'DROP', 'DELETE', 'INSERT', 'UPDATE']
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Valida formato de telefone brasileiro"""
        pattern = r'^\+?55?\s?(\d{2})\s?9?\d{4}-?\d{4}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nome de arquivo para prevenir path traversal"""
        # Remove caracteres perigosos
        filename = re.sub(r'[^\w\s.-]', '', filename)
        # Remove path traversal
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        return filename


sanitizer = InputSanitizer()


# =============================================================================
# SECURITY HEADERS - Headers HTTP de segurança
# =============================================================================
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}


async def add_security_headers(request: Request, call_next):
    """Middleware para adicionar headers de segurança"""
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


# =============================================================================
# API KEY MANAGEMENT - Gestão segura de chaves de API
# =============================================================================
class APIKeyManager:
    """Gerenciador de chaves de API"""
    
    def __init__(self):
        self.keys: Dict[str, Dict[str, Any]] = {}
    
    def generate_key(self, user_id: str, name: str) -> str:
        """Gera uma nova chave de API"""
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        self.keys[api_key] = {
            "user_id": user_id,
            "name": name,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "is_active": True
        }
        logger.info(f"Nova API key gerada para usuário {user_id}: {name}")
        return api_key
    
    def validate_key(self, api_key: str) -> bool:
        """Valida uma chave de API"""
        if api_key not in self.keys:
            return False
        
        key_data = self.keys[api_key]
        if not key_data["is_active"]:
            return False
        
        # Atualiza último uso
        key_data["last_used"] = datetime.utcnow()
        return True
    
    def revoke_key(self, api_key: str) -> bool:
        """Revoga uma chave de API"""
        if api_key in self.keys:
            self.keys[api_key]["is_active"] = False
            logger.warning(f"API key revogada: {api_key}")
            return True
        return False


api_key_manager = APIKeyManager()


# =============================================================================
# SECURITY LOGGER - Logging de eventos de segurança
# =============================================================================
class SecurityLogger:
    """Logger especializado para eventos de segurança"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        handler = logging.FileHandler("logs/security.log")
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_login_attempt(self, username: str, ip: str, success: bool):
        """Registra tentativa de login"""
        status = "SUCESSO" if success else "FALHA"
        self.logger.info(f"Login {status} - User: {username}, IP: {ip}")
    
    def log_suspicious_activity(self, activity: str, ip: str, details: str = ""):
        """Registra atividade suspeita"""
        self.logger.warning(f"Atividade suspeita - {activity} - IP: {ip} - {details}")
    
    def log_data_access(self, user_id: str, resource: str, action: str):
        """Registra acesso a dados"""
        self.logger.info(f"Acesso a dados - User: {user_id}, Resource: {resource}, Action: {action}")
    
    def log_rate_limit_exceeded(self, ip: str, endpoint: str):
        """Registra excesso de rate limit"""
        self.logger.warning(f"Rate limit excedido - IP: {ip}, Endpoint: {endpoint}")


security_logger = SecurityLogger()


# =============================================================================
# PASSWORD SECURITY - Segurança de senhas
# =============================================================================
class PasswordValidator:
    """Validador de força de senha"""
    
    @staticmethod
    def validate_strength(password: str) -> tuple[bool, list[str]]:
        """
        Valida a força da senha
        Retorna: (é_válida, lista_de_erros)
        """
        errors = []
        
        if len(password) < 8:
            errors.append("Senha deve ter no mínimo 8 caracteres")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Senha deve conter pelo menos uma letra maiúscula")
        
        if not re.search(r'[a-z]', password):
            errors.append("Senha deve conter pelo menos uma letra minúscula")
        
        if not re.search(r'\d', password):
            errors.append("Senha deve conter pelo menos um número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Senha deve conter pelo menos um caractere especial")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def check_common_passwords(password: str) -> bool:
        """Verifica se a senha está na lista de senhas comuns"""
        common_passwords = [
            "password", "123456", "12345678", "qwerty", "abc123",
            "monkey", "1234567", "letmein", "trustno1", "dragon",
            "baseball", "111111", "iloveyou", "master", "sunshine"
        ]
        return password.lower() not in common_passwords


password_validator = PasswordValidator()


# =============================================================================
# REQUEST VALIDATION - Validação de requisições
# =============================================================================
async def validate_request_size(request: Request, max_size: int = 10 * 1024 * 1024):
    """Valida o tamanho da requisição (max 10MB por padrão)"""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Requisição muito grande"
        )


def require_https(func):
    """Decorator que força HTTPS em produção"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not settings.DEBUG and request.url.scheme != "https":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="HTTPS obrigatório"
            )
        return await func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# IP BLOCKING - Bloqueio de IPs suspeitos
# =============================================================================
class IPBlocker:
    """Gerenciador de bloqueio de IPs"""
    
    def __init__(self):
        self.blocked_ips: Dict[str, datetime] = {}
        self.failed_attempts: Dict[str, int] = {}
    
    def is_blocked(self, ip: str) -> bool:
        """Verifica se um IP está bloqueado"""
        if ip in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[ip]:
                return True
            else:
                # Tempo de bloqueio expirou
                del self.blocked_ips[ip]
                self.failed_attempts[ip] = 0
        return False
    
    def record_failed_attempt(self, ip: str, max_attempts: int = 5):
        """Registra tentativa falha e bloqueia se necessário"""
        self.failed_attempts[ip] = self.failed_attempts.get(ip, 0) + 1
        
        if self.failed_attempts[ip] >= max_attempts:
            # Bloqueia por 30 minutos
            self.blocked_ips[ip] = datetime.utcnow() + timedelta(minutes=30)
            security_logger.log_suspicious_activity(
                "IP bloqueado por múltiplas tentativas falhas",
                ip,
                f"Tentativas: {self.failed_attempts[ip]}"
            )
            return True
        return False
    
    def clear_attempts(self, ip: str):
        """Limpa tentativas falhas após sucesso"""
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]


ip_blocker = IPBlocker()


# =============================================================================
# MIDDLEWARE DE SEGURANÇA
# =============================================================================
async def security_middleware(request: Request, call_next):
    """Middleware central de segurança"""
    
    # Verifica bloqueio de IP
    client_ip = get_remote_address(request)
    if ip_blocker.is_blocked(client_ip):
        security_logger.log_suspicious_activity("Acesso negado - IP bloqueado", client_ip)
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Acesso bloqueado temporariamente"}
        )
    
    # Valida tamanho da requisição
    await validate_request_size(request)
    
    # Continua com a requisição
    response = await call_next(request)
    
    return response
