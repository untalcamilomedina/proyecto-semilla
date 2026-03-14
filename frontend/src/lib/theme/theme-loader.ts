import { ThemeConfig } from "./theme-schema";

/**
 * Generates a CSS string containing all custom properties for a given theme.
 * This string is injected into the DOM by the ThemeProvider.
 */
export function generateThemeCssVariables(theme: ThemeConfig): string {
  return `
    :root {
      /* Colors: Light Mode */
      --background: ${theme.colors.light.background};
      --foreground: ${theme.colors.light.foreground};
      --primary: ${theme.colors.light.primary};
      --primary-foreground: ${theme.colors.light["primary-foreground"]};
      --muted: ${theme.colors.light.muted};
      --muted-foreground: ${theme.colors.light["muted-foreground"]};
      --border: ${theme.colors.light.border};
      --glass-bg: ${theme.colors.light["glass-bg"]};
      --glass-border: ${theme.colors.light["glass-border"]};
      
      /* Typography */
      --font-heading: ${theme.typography.fontFamily.heading};
      --font-body: ${theme.typography.fontFamily.body};
      --font-mono: ${theme.typography.fontFamily.mono};
      
      /* Spacing & Effects */
      --radius: ${theme.spacing.radius};
      --glass-blur: ${theme.effects.blur};
    }

    .dark {
      /* Colors: Dark Mode */
      --background: ${theme.colors.dark.background};
      --foreground: ${theme.colors.dark.foreground};
      --primary: ${theme.colors.dark.primary};
      --primary-foreground: ${theme.colors.dark["primary-foreground"]};
      --muted: ${theme.colors.dark.muted};
      --muted-foreground: ${theme.colors.dark["muted-foreground"]};
      --border: ${theme.colors.dark.border};
      --glass-bg: ${theme.colors.dark["glass-bg"]};
      --glass-border: ${theme.colors.dark["glass-border"]};
    }
  `;
}
