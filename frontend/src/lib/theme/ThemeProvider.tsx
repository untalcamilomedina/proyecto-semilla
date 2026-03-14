"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import { ThemeConfig } from "./theme-schema";
import { generateThemeCssVariables } from "./theme-loader";
import defaultThemeRaw from "./default-theme.json";

// Cast the imported JSON to our validated schema type
const defaultTheme = defaultThemeRaw as ThemeConfig;

interface ThemeProviderProps {
  children: React.ReactNode;
  /**
   * Optional custom theme. If omitted, uses default-theme.json.
   * In a multi-tenant app, you would pass the tenant's theme JSON here.
   */
  customTheme?: ThemeConfig;
}

/**
 * Global Theme Provider.
 * Wraps the application to provide light/dark mode toggling (via next-themes)
 * and injects the dynamic CSS variables generated from the active Theme JSON.
 */
export function ThemeProvider({ children, customTheme }: ThemeProviderProps) {
  const activeTheme = customTheme || defaultTheme;
  const cssVariables = generateThemeCssVariables(activeTheme);

  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {/* Inject dynamic theme variables globally */}
      <style dangerouslySetInnerHTML={{ __html: cssVariables }} />
      {children}
    </NextThemesProvider>
  );
}
