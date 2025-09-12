# API de Artículos

Este documento describe el diseño de la API para la gestión de artículos.

## 1. Modelo de Datos

El modelo de datos para los artículos se definirá en `backend/app/models/article.py` y tendrá la siguiente estructura:

```python
# backend/app/models/article.py

import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum as SQLAlchemyEnum, ForeignKey, String, Text, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class ArticleStatus(enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(SQLAlchemyEnum(ArticleStatus), nullable=False, default=ArticleStatus.draft)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User")

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title}')>"
```

## 2. Esquemas Pydantic

Los esquemas Pydantic para la validación de datos de la API se definirán en `backend/app/schemas/article.py`.

```python
# backend/app/schemas/article.py

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.article import ArticleStatus

class ArticleBase(BaseModel):
    title: str
    content: str
    status: Optional[ArticleStatus] = ArticleStatus.draft

class ArticleCreate(ArticleBase):
    author_id: UUID

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[ArticleStatus] = None

class ArticleResponse(ArticleBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## 3. Endpoints de la API

Los endpoints de la API para gestionar los artículos se definirán en `backend/app/api/v1/endpoints/articles.py`.

### `POST /api/v1/articles/`

-   **Descripción:** Crear un nuevo artículo.
-   **Método HTTP:** `POST`
-   **Cuerpo de la solicitud:** `ArticleCreate`
-   **Respuesta:** `ArticleResponse`

### `GET /api/v1/articles/`

-   **Descripción:** Obtener una lista de artículos.
-   **Método HTTP:** `GET`
-   **Parámetros de consulta:** `skip: int = 0`, `limit: int = 100`
-   **Respuesta:** `List[ArticleResponse]`

### `GET /api/v1/articles/{article_id}`

-   **Descripción:** Obtener un artículo por su ID.
-   **Método HTTP:** `GET`
-   **Parámetro de ruta:** `article_id: UUID`
-   **Respuesta:** `ArticleResponse`

### `PUT /api/v1/articles/{article_id}`

-   **Descripción:** Actualizar un artículo existente.
-   **Método HTTP:** `PUT`
-   **Parámetro de ruta:** `article_id: UUID`
-   **Cuerpo de la solicitud:** `ArticleUpdate`
-   **Respuesta:** `ArticleResponse`

### `DELETE /api/v1/articles/{article_id}`

-   **Descripción:** Eliminar un artículo.
-   **Método HTTP:** `DELETE`
-   **Parámetro de ruta:** `article_id: UUID`
-   **Respuesta:** `{"message": "Article deleted successfully"}`

## 4. Integración del Router

El nuevo router de artículos se debe integrar en el router principal de la API en `backend/app/api/v1/router.py`.

```python
# backend/app/api/v1/router.py

# ... (importaciones existentes)
from app.api.v1.endpoints import articles

# ... (código existente)

api_router.include_router(
    articles.router,
    prefix="/articles",
    tags=["articles"]
)