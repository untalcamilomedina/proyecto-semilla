# DESIGN_SYSTEM.md

> **Estilo Gráfico: Minimalismo Industrial (Notion-esque)**

Este documento define los lineamientos para la interfaz de usuario de **AppNotion**.
Basado en "Glassmorphism Industrial" pero adaptado a una paleta estricta de **Blanco y Negro**.

## 1. Principios de Diseño

- **Minimalismo Puro:** Menos es más. Espacios en blanco generosos.
- **Blanco y Negro:** Sin colores de acento vibrantes (salvo estados de error/éxito muy sutiles).
- **Tipografía Funcional:** Jerarquía clara usando pesos y tamaños, no colores.
- **Bordes y Líneas:** Uso de bordes finos (1px) sutiles para delimitar áreas, estilo Notion.

## 2. Paleta de Colores (Tokens)

```css
:root {
  /* Fondo */
  --bg-primary: #ffffff;
  --bg-secondary: #f7f7f7; /* Gris muy claro para sidebar/fondos */

  /* Texto */
  --text-primary: #000000;
  --text-secondary: #666666;
  --text-tertiary: #999999;

  /* Bordes */
  --border-light: #e0e0e0;
  --border-strong: #000000;

  /* Interacción */
  --hover-bg: #f0f0f0;
  --active-bg: #e5e5e5;
}

/* Modo Oscuro (Si aplica) */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #191919; /* Notion Dark */
    --bg-secondary: #202020;
    --text-primary: #ffffff;
    --text-secondary: #9b9b9b;
    --border-light: #2f2f2f;
  }
}
```

## 3. Tipografía

- **Fuentes:** Inter, Roboto, o System Font Stack (San Francisco/Segoe UI).
- **Títulos:** Negrita (Bold), tracking ajustado (-0.02em).
- **Cuerpo:** Regular, altura de línea cómoda (1.5).

## 4. Componentes Clave

### Botones

- **Primario:** Fondo Negro, Texto Blanco. Sin borde. Border-radius sutil (4px o 6px).
  - _Hover:_ Opacidad 0.9.
- **Secundario:** Fondo Transparente, Borde Gris Claro, Texto Negro.
  - _Hover:_ Fondo Gris Muy Claro.

### Tarjetas (Cards)

- Planas (Flat) o con borde muy sutil (`1px solid var(--border-light)`).
- **Sombra:** Mínima o inexistente. Preferir bordes para separar.

### Inputs

- Fondo transparente o gris muy claro.
- Borde inferior o borde completo muy fino (`#E0E0E0`).
- Focus: Borde Negro (`#000000`).

## 5. Layout (Inspiración Notion)

- **Sidebar:** Gris claro, lista de herramientas/páginas.
- **Contenido:** Blanco puro, centrado, ancho de lectura optimizado (max-w-3xl para texto).
- **Marketplace Grid:** Grid limpio de tarjetas con iconos minimalistas (blanco y negro).

## 6. Iconografía

- Iconos de línea fina (1.5px stroke).
- Estilo: Lucide React, Phosphor Icons (Thin/Light).
- Color: `#000000` o `#666666`.
