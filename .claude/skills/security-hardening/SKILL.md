---
name: security-hardening
description: Corrige vulnerabilidades de seguridad en Django/Next.js SaaS - secrets, OAuth, CSRF, auth, encryption
author: Mayordomos Dev Team
version: 1.0.0
---

# Skill: Security Hardening para BlockFlow SaaS

Esta skill guia la correccion sistematica de vulnerabilidades de seguridad en el stack Django + Next.js, cubriendo secrets management, OAuth flows, CSRF protection, authentication hardening y encryption key isolation.

## Prerrequisitos

- [ ] Auditoria de seguridad completada con hallazgos categorizados
- [ ] Acceso al codebase backend (`src/`) y frontend (`frontend/src/`)
- [ ] Conocimiento de las variables de entorno actuales (`local.env`)

## Cuando Usar

Usar esta skill cuando:
- Se detectan secretos hardcodeados o expuestos en git
- OAuth flows carecen de state validation
- CSRF tokens no se envian en requests mutantes
- Encryption keys estan derivadas de SECRET_KEY
- Debug/profiling endpoints estan expuestos en produccion

## Proceso

### Paso 1: Secrets Management

**Problema:** `local.env` trackeado en git, SECRET_KEY con default inseguro.

**Archivos a modificar:**
- `/.gitignore` - Agregar `local.env`
- `/src/config/settings/base.py` - Remover default de SECRET_KEY
- `/src/config/settings/prod.py` - Forzar SECRET_KEY requerido

```bash
# Remover local.env del tracking sin borrarlo
git rm --cached local.env
```

```gitignore
# Agregar a .gitignore
local.env
*.env.local
celerybeat-schedule
```

```python
# base.py - Sin default inseguro
SECRET_KEY = env.str("DJANGO_SECRET_KEY")  # Sin default, falla si no existe

# prod.py - Validacion explicita
import django
from django.core.exceptions import ImproperlyConfigured

if SECRET_KEY in ("changeme", "dev-secret-key-12345", ""):
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set to a secure value in production")
```

### Paso 2: Encryption Key Isolation

**Problema:** Fernet key derivada de SECRET_KEY[:32] con padding debil.

**Archivo:** `/src/integrations/models.py`

```python
import os
import base64
from cryptography.fernet import Fernet

def get_cipher_suite():
    """Usa una clave dedicada, independiente del SECRET_KEY."""
    encryption_key = os.environ.get("FIELD_ENCRYPTION_KEY")
    if not encryption_key:
        raise ImproperlyConfigured(
            "FIELD_ENCRYPTION_KEY must be set. "
            "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    return Fernet(encryption_key.encode())
```

**Agregar a `local.env`:**
```env
# Generar con: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
FIELD_ENCRYPTION_KEY=<generated-key>
```

### Paso 3: OAuth State Validation

**Problema:** State predecible `user_{id}` y sin validacion en callback.

**Archivo:** `/src/integrations/oauth/views.py`

```python
import secrets
from django.contrib.sessions.backends.db import SessionStore

class OAuthStartView(APIView):
    def get(self, request, provider):
        # Generar state criptograficamente seguro
        state = secrets.token_urlsafe(32)
        request.session[f"oauth_state_{provider}"] = state
        request.session.save()

        adapter = get_adapter(provider)
        auth_url = adapter.get_authorization_url(state=state)
        return Response({"authorization_url": auth_url})


class OAuthCallbackView(APIView):
    def get(self, request, provider):
        received_state = request.GET.get("state")
        expected_state = request.session.pop(f"oauth_state_{provider}", None)

        if not received_state or received_state != expected_state:
            return Response(
                {"error": "Invalid OAuth state. Please try again."},
                status=400
            )

        code = request.GET.get("code")
        if not code:
            return Response({"error": "Missing authorization code."}, status=400)

        # Continuar con el exchange...
```

### Paso 4: CSRF Token en Frontend

**Problema:** Frontend nunca envia X-CSRFToken en mutations.

**Archivo:** `/frontend/src/lib/api.ts`

```typescript
// Funcion para obtener CSRF token
async function getCsrfToken(): Promise<string> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/csrf/`,
    { credentials: "include" }
  );
  const data = await response.json();
  return data.csrfToken;
}

// Cache del CSRF token
let csrfToken: string | null = null;

export async function ensureCsrfToken(): Promise<string> {
  if (!csrfToken) {
    csrfToken = await getCsrfToken();
  }
  return csrfToken;
}

// Resetear en caso de 403
export function resetCsrfToken() {
  csrfToken = null;
}
```

**En cada funcion mutante (apiPost, apiPatch, apiDelete):**
```typescript
const token = await ensureCsrfToken();
headers["X-CSRFToken"] = token;
```

### Paso 5: Gate Debug/Profiling en Produccion

**Archivos:**
- `/src/config/urls.py` - Condicionar debug endpoint
- `/src/config/settings/base.py` - Condicionar Silk

```python
# urls.py
from django.conf import settings

urlpatterns = [
    # ... rutas normales
]

if settings.DEBUG:
    urlpatterns += [
        path("debug/error/", trigger_error),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
```

```python
# base.py - Silk condicional
INSTALLED_APPS_BASE = [...]

if DEBUG:
    INSTALLED_APPS_BASE += ["silk"]

INSTALLED_APPS = INSTALLED_APPS_BASE

# Middleware condicional
MIDDLEWARE_BASE = [...]
if DEBUG:
    MIDDLEWARE_BASE.insert(7, "silk.middleware.SilkyMiddleware")
MIDDLEWARE = MIDDLEWARE_BASE
```

### Paso 6: Remover BasicAuthentication de Produccion

**Archivo:** `/src/config/settings/base.py`

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.authentication.ApiKeyAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # BasicAuthentication REMOVIDO
    ],
    # ...
}
```

### Paso 7: Password Validators

**Archivo:** `/src/config/settings/base.py`

```python
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
```

### Paso 8: Sanitizar Zustand Store (Frontend)

**Archivo:** `/frontend/src/stores/onboarding.ts`

```typescript
// NUNCA persistir secretos
partialize: (state) => ({
    organization: state.organization,
    language: state.language,
    step: state.step,
    // EXCLUIR: user.password, stripe.secretKey, stripe.webhookSecret
    user: state.user ? { ...state.user, password: undefined } : state.user,
    stripe: state.stripe ? {
        enabled: state.stripe.enabled,
        publicKey: state.stripe.publicKey,
        // secretKey y webhookSecret EXCLUIDOS
    } : state.stripe,
}),
```

### Paso 9: Readiness Probe Real

**Archivo:** `/src/config/urls.py`

```python
from django.db import connection
from django.core.cache import cache

def readyz(request):
    checks = {}
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "fail"

    try:
        cache.set("_health", "1", 10)
        checks["cache"] = "ok" if cache.get("_health") == "1" else "fail"
    except Exception:
        checks["cache"] = "fail"

    all_ok = all(v == "ok" for v in checks.values())
    return JsonResponse(
        {"status": "ready" if all_ok else "degraded", "checks": checks},
        status=200 if all_ok else 503,
    )
```

## Checklist de Verificacion

### Obligatorio
- [ ] `local.env` removido de git tracking
- [ ] `local.env` agregado a `.gitignore`
- [ ] SECRET_KEY sin default inseguro
- [ ] FIELD_ENCRYPTION_KEY como variable separada
- [ ] OAuth state usa `secrets.token_urlsafe(32)`
- [ ] OAuth callback valida state contra session
- [ ] Frontend envia X-CSRFToken en POST/PATCH/DELETE
- [ ] `debug/error/` solo disponible con DEBUG=True
- [ ] django-silk solo cargado con DEBUG=True
- [ ] BasicAuthentication removido de DEFAULT_AUTHENTICATION_CLASSES
- [ ] AUTH_PASSWORD_VALIDATORS configurados
- [ ] Stripe secrets excluidos del Zustand persist
- [ ] Password excluido del Zustand persist
- [ ] Readiness probe verifica DB y Redis

### Recomendado
- [ ] Rate limiting en `/api/v1/login`
- [ ] API key scopes enforceados en authentication
- [ ] `except Exception` reemplazado con errores especificos en integration views
- [ ] CORS configurado en `prod.py`

## Errores Comunes

### Error: "DJANGO_SECRET_KEY not set" al iniciar en dev
**Causa:** Se removio el default de SECRET_KEY
**Solucion:** Asegurar que `local.env` contiene `DJANGO_SECRET_KEY=dev-secret-key-12345` y que `ENV_FILE=local.env` esta seteado

### Error: CSRF 403 despues de implementar tokens
**Causa:** Cookie no se envia por dominio cruzado
**Solucion:** Verificar `CSRF_TRUSTED_ORIGINS` incluye `http://localhost:3010`

### Error: OAuth tokens no se descifran post-migration
**Causa:** Se cambio la clave de encriptacion
**Solucion:** Crear migration que re-encripte tokens con la nueva clave antes de borrar la vieja

## Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Fernet Symmetric Encryption](https://cryptography.io/en/latest/fernet/)

---

*Ultima actualizacion: 2026-02-05*
