# 🎨 Design System & Guidelines: "Glassmorphism Industrial"

Este documento contiene los lineamientos gráficos, técnicos y las instrucciones (prompts) para replicar el estilo elegante y moderno de "mi ultima web" en futuros proyectos.

---

## 📋 Instrucción Master (Prompt para IA)

Copia y pega esto al iniciar tu nuevo proyecto para establecer el estilo de inmediato:

> **Rol:** Eres un Diseñador UI/UX Senior y Desarrollador Frontend experto.
> **Objetivo:** Crear un sitio web corporativo de alto impacto visual, elegante y minimalista.
> **Estilo Gráfico:** "Modern Glassmorphism" (Efecto vidrio esmerilado).
>
> **Extracción de Identidad Visual (CRÍTICO):**
> Antes de diseñar, DEBES preguntar al usuario:
> 1.  "¿Cuáles son los colores principales de tu marca?"
> 2.  "¿Tienes una URL actual de la cual pueda extraer estos colores?"
>
> **Si el usuario da una URL:** Navega a ella, extrae el color primario (botones/logo) y secundario (textos/títulos), y úsalos en la paleta.
> **Si el usuario da los colores:** Úsalos directamente.
> **Si no hay info:** Propón una paleta elegante acorde a la industria del cliente.
>
> **Reglas de Diseño (Estrictas):**
> 1.  **Glassmorphism:** Usa fondos translúcidos (`backdrop-filter: blur`) con bordes sutiles blancos para contenedores de texto, tarjetas y menús. No uses fondos sólidos opacos para estos elementos (salvo inputs).
> 2.  **Fondo:** El `body` debe ser oscuro (`#1A1A1D` o similar) o usar imágenes de fondo de alta calidad, oscurecidas para contraste. NUNCA uses fondo blanco plano para el sitio.
> 3.  **Colores:**
>     *   **Primario (Acento):** El extraído de la marca para botones y llamadas a la acción.
>     *   **Sin Degradados:** Evita degradados complejos en botones o textos (estilo "WordArt"). Mantén los colores planos ("Flat").
> 4.  **Tipografía:** Usa fuentes modernas de Google Fonts.
>     *   Títulos: *Outfit*, *Montserrat* o *Space Grotesk* (Sans-serif geométricas).
>     *   Cuerpo: *Inter*, *Roboto* o *Manrope* (Legibilidad máxima).
> 5.  **Imágenes:** Deben ser de alta resolución, estilo cinemático/industrial.
> 6.  **Logos:** Si el logo es oscuro, usa `filter: brightness(0) invert(1)` para volverlo blanco puro y mejorar la elegancia.
>
> **Stack Técnico:**
> *   HTML5 Semántico.
> *   CSS3 Moderno (Variables CSS, Flexbox, Grid).
> *   JavaScript Vanilla (Sin frameworks pesados).
> *   Mobile First & Responsive.

---

## 🛠️ Especificaciones Técnicas (Design Tokens)

### 1. Variables CSS Base
Copia estas variables en tu archivo CSS para tener la base lista. **Recuerda reemplazar los colores por los de tu marca.**

```css
:root {
    /* 🎨 Paleta de Colores (DEFINIR SEGÚN MARCA) */
    --primary-color: #XXXXXX;  /* <--- REEMPLAZAR con color principal */
    --secondary-color: #XXXXXX; /* <--- REEMPLAZAR con color secundario */
    --bg-dark: #1A1A1D;         /* Fondo Principal Oscuro */
    
    /* 🌫️ Sistema Glassmorphism (No modificar) */
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-blur: 15px;
    --text-color: #F8F9FA;
    --text-muted: #CCCCCC;
    
    /* 🔤 Tipografía */
    --font-heading: 'Outfit', sans-serif;
    --font-body: 'Inter', sans-serif;
}
```

### 2. Clases Utilitarias "Glass"
El núcleo del diseño. Usa estas clases para dar el efecto.

```css
/* Contenedor base de vidrio */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    color: var(--text-color);
}

/* Efecto Hover para interactividad */
.glass-card:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-5px);
    transition: all 0.3s ease;
}

/* Navbar efecto vidrio */
.glossy-nav {
    background: rgba(26, 26, 29, 0.85); /* Un poco más oscuro para legibilidad */
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--glass-border);
}
```

### 3. Animaciones
Para dar el toque "Premium", usa animaciones de entrada.

```css
/* Scroll Reveal (Clases JS requeridas: .hidden y .visible) */
.hidden {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.8s ease-out;
}

.visible {
    opacity: 1;
    transform: translateY(0);
}
```

---

## 📸 Guía de Activos (Assets)

1.  **Logo**:
    *   Formato: PNG transparente o SVG.
    *   Tratamiento: Si el fondo es oscuro, el logo debe ser **BLANCO**.
    *   CSS Fix: `.logo img { filter: brightness(0) invert(1); }`
2.  **Fotografía**:
    *   Estilo: Oscuro, alto contraste, profundidad de campo (fondo borroso).
    *   Uso: Como `background-image` con un overlay oscuro para que el texto resalte.
    *   *Ejemplo CSS:* `background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('foto.jpg');`

---

## 🚀 Checklist de Calidad
Antes de entregar el nuevo proyecto:
- [ ] ¿El menú es legible sobre cualquier fondo?
- [ ] ¿Los botones de acción (Primary) resaltan claramente?
- [ ] ¿Funciona el efecto "glass" en Safari/iPhone? (`-webkit-backdrop-filter` presente).
- [ ] ¿Las imágenes cargan rápido? (Formato WebP).
- [ ] ¿Hay espacio suficiente (padding) dentro de las tarjetas de vidrio? (No amontonar texto).
