---
name: audit-frontend-ux
description: Guía de auditoría profesional para validar calidad, accesibilidad, internacionalización y responsividad.
author: AppNotion QA Team
version: 1.0.0
---

# Skill: Auditoría UX/UI Frontend

Esta skill define el proceso estándar para realizar una auditoría de calidad ("Quality Assurance") visual y funcional del Frontend. Se debe ejecutar antes de cualquier lanzamiento importante.

## Prerrequisitos

- [ ] Servidor de desarrollo corriendo (`npm run dev` en puerto 3000).
- [ ] Credenciales de usuario de prueba (Demo/Admin).
- [ ] Agente Web (Browser Tool) disponible.

## Áreas de Auditoría

### 1. Integridad Visual (Visual Regression)

Validar que la interfaz no tenga elementos rotos, desalineados o superpuestos.

- **Desktop (1920x1080)**: Verificar layout de Sidebar, Tablas y Gráficos.
- **Mobile (390x844)**: Verificar colapso de Sidebar, hamburguesas, y tarjetas responsivas.

### 2. Internacionalización (i18n)

Validar que **NO** existan textos hardcodeados.

- Buscar strings crudos en la UI.
- Validar formato de fechas y monedas según el locale.

### 3. Accesibilidad (a11y)

Validar cumplimiento básico de WCAG 2.1.

- Focus visible al navegar con tabulador.
- Etiquetas `aria-label` en botones de solo ícono.
- **Botones de Acción**: Texto con alto contraste (blanco sobre fondo oscuro) y alineación horizontal (icono + texto).

### 4. Consola y Red

Validar ausencia de errores técnicos.

- **Console Errors**: React Warnings (keys duplicadas, useEffect loops), 404s de recursos.
- **Network**: Requests fallidos (500/400) en carga inicial.

## Proceso de Ejecución (Paso a Paso)

### Paso 1: Login & Auth Flow

1.  Navegar a `/login`.
2.  Probar credenciales inválidas (debe mostrar error).
3.  Login exitoso -> Redirección a `/dashboard`.

### Paso 2: Navegación Core

Recorrer las páginas principales y tomar capturas para evidencia:

1.  **Dashboard**: `/dashboard`
2.  **Integrations**: `/integrations`
3.  **Diagrams**: `/diagrams`
4.  **Editor**: `/diagrams/[id]` (Interacción básica con Canvas).
5.  **Settings**: `/settings`

### Paso 3: Mobile Check

1.  Redimensionar navegador a móvil.
2.  Verificar que el menú sea accesible.
3.  Verificar que las tablas no rompan el layout (scroll horizontal o cards).

## Checklist de Verificación Final

- [ ] Login funcional con feedback de error.
- [ ] No hay errores rojos en la consola del navegador.
- [ ] Layout Mobile utilizable (sin overflow horizontal).
- [ ] Glassmorphism consistente (fondos no opacos innecesariamente).
- [ ] Todas las páginas protegidas redirigen si no hay sesión.

## Errores Comunes y Soluciones

### Error: "Hydration Mismatch"

**Causa:** Renderizado diferente en Servidor vs Cliente (ej. Fechas, LocalStorage).
**Solución:** Usar `useEffect` para renderizar datos dependientes del cliente o `suppressHydrationWarning`.

### Error: "Textos en Inglés mezclados"

**Causa:** Falta key en `es.json`.
**Solución:** Usar skill `add-i18n-keys`.

### Error: "Layout roto en móvil"

**Causa:** Uso de `w-full` o anchos fijos (`w-[500px]`).
**Solución:** Usar `max-w-full`, `flex-wrap` o `hidden md:block`.
