import { z } from "zod";

/**
 * Zod schema defining the structure of a Theme JSON.
 * Any tenant connecting a custom theme must adhere to this schema.
 */
export const themeSchema = z.object({
  name: z.string(),
  version: z.string(),
  colors: z.object({
    light: z.object({
      background: z.string(),
      foreground: z.string(),
      primary: z.string(),
      "primary-foreground": z.string(),
      muted: z.string(),
      "muted-foreground": z.string(),
      border: z.string(),
      "glass-bg": z.string(),
      "glass-border": z.string(),
    }),
    dark: z.object({
      background: z.string(),
      foreground: z.string(),
      primary: z.string(),
      "primary-foreground": z.string(),
      muted: z.string(),
      "muted-foreground": z.string(),
      border: z.string(),
      "glass-bg": z.string(),
      "glass-border": z.string(),
    }),
  }),
  typography: z.object({
    fontFamily: z.object({
      heading: z.string(),
      body: z.string(),
      mono: z.string(),
    }),
    scale: z.string(),
  }),
  spacing: z.object({
    radius: z.string(),
    radiusLg: z.string(),
    radiusFull: z.string(),
  }),
  effects: z.object({
    glass: z.boolean(),
    animations: z.boolean(),
    blur: z.string(),
  }),
});

export type ThemeConfig = z.infer<typeof themeSchema>;
