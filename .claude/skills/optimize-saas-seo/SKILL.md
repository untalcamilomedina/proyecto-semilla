---
name: optimize-saas-seo
description: Guía experta para optimizar SEO técnico, on-page y metadatos en SaaS B2B usando Next.js 14+ y Metadata API.
author: BlockFlow Team
version: 1.0.0
---

# Skill: Optimización SEO para SaaS (BlockFlow)

Esta skill guía la implementación de estrategias SEO avanzadas enfocadas en productos SaaS, asegurando indexabilidad, performance y estructura semántica correcta en aplicaciones Next.js.

## Prerrequisitos

- [ ] La página debe ser pública (no `useAuth` sin renderizado condicional de metadata) o una Landing Page.
- [ ] Tener acceso a `messages/{locale}.json` para textos localizados.
- [ ] Tener definidos los assets gráficos (OG Images) en `public/images/og/`.

## Cuándo Usar

Usar esta skill cuando:

- Creas una nueva Landing Page o página de marketing.
- Optimizas páginas de documentación o blog.
- Necesitas configurar `sitemap.xml` o `robots.txt`.
- Mejoras el compartimiento en redes sociales (Open Graph / Twitter Cards).

NO usar cuando:

- Trabajas en rutas protegidas del Dashboard (requieren `noindex` por defecto en layout).

## Proceso

### Paso 1: Configurar Metadata Estática o Dinámica

Next.js 14 usa Metadata API. Evita `Head` de `next/head`.

```typescript
// src/app/[locale]/features/page.tsx
import { Metadata } from "next";
import { getTranslations } from "next-intl/server";

export async function generateMetadata({
  params: { locale },
}): Promise<Metadata> {
  const t = await getTranslations({ locale, namespace: "features" });

  return {
    title: t("meta.title"), // "Gestión de Roles | BlockFlow"
    description: t("meta.description"),
    alternates: {
      canonical: `https://blockflow.so/${locale}/features`,
      languages: {
        es: `https://blockflow.so/es/features`,
        en: `https://blockflow.so/en/features`,
      },
    },
    openGraph: {
      title: t("meta.title"),
      description: t("meta.description"),
      url: `https://blockflow.so/${locale}/features`,
      siteName: "BlockFlow",
      images: [
        {
          url: "https://blockflow.so/images/og/features-og.png",
          width: 1200,
          height: 630,
        },
      ],
      locale: locale,
      type: "website",
    },
  };
}
```

### Paso 2: Datos Estructurados (JSON-LD)

Para SaaS, es vital marcar el `SoftwareApplication` o `Organization`.

```typescript
// Componente: components/seo/JsonLd.tsx
export function JsonLd({ data }: { data: Record<string, any> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

// Uso en Page
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "BlockFlow",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "29.00",
    "priceCurrency": "USD"
  }
};
```

### Paso 3: Optimización de Performance (Core Web Vitals)

1. **Fuentes**: Usar `next/font` para evitar CLS (Cumulative Layout Shift).
2. **Imágenes**: Usar `<Image />` con `priority` si está en el "Above the Fold".
3. **Scripts**: Usar `next/script` con `strategy="lazyOnload"` para analíticas.

## Checklist de Verificación Publicación

### Crítico

- [ ] **Title Tag**: Único, < 60 caracteres, incluye keyword principal.
- [ ] **Meta Description**: Única, < 160 caracteres, incluye CTA.
- [ ] **H1 Único**: Solo un H1 por página.
- [ ] **Canonical URL**: Apunta a sí misma (self-referencing) o a la versión original.
- [ ] **Hreflang**: Correctamente configurado para `es` y `en`.

### Redes Sociales

- [ ] **OG Image**: Existe y carga correctamente (1200x630px).
- [ ] **Twitter Card**: Configurada como `summary_large_image`.

### Técnico

- [ ] **JSON-LD**: Valido en Rich Results Test.
- [ ] **Noindex**: Asegurar que NO esté presente en páginas públicas.
- [ ] **Sitemap**: La URL está incluida en `sitemap.xml`.

## Errores Comunes

### Error: "Missing Metadata exporting"

**Causa**: Usar `generateMetadata` en un componente Cliente (`use client`).
**Solución**: Mover la metadata a `layout.tsx` o `page.tsx` (Server Components). Pasar datos al cliente como props si es necesario.

### Error: Duplicidad de Contenido

**Causa**: Acceder a `/es/ruta` y `/es/ruta/` (slash final).
**Solución**: Configurar redirecciones 301 en `next.config.js` o middleware para normalizar trailing slashes.

## Referencias

- [Next.js Metadata API](https://nextjs.org/docs/app/building-your-application/optimizing/metadata)
- [Schema.org SoftwareApplication](https://schema.org/SoftwareApplication)
- [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
