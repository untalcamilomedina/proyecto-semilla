"use client";

import { useTranslations } from "next-intl";
import { GlassButton } from "@/components/ui/glass/GlassButton";

/**
 * Internally accessible Design System page.
 * Acts as a live, in-app catalog of the JSON-driven theme.
 */
export default function DesignSystemPage() {
  const t = useTranslations("common");

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500 max-w-5xl mx-auto py-10">
      <header className="space-y-2">
        <h1 className="text-4xl font-heading font-bold text-foreground">
          Configurable Design System
        </h1>
        <p className="text-muted-foreground text-lg">
          Live catalog showing how semantic JSON tokens apply strictly to components.
        </p>
      </header>

      <section className="space-y-6">
        <div className="border-b border-border pb-2">
          <h2 className="text-2xl font-heading font-semibold text-foreground">GlassButton</h2>
          <p className="text-sm text-text-tertiary mt-1">
            Mobile-first sizes (min 44px h-11 default), strict JSON mapping.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Variants */}
          <div className="space-y-4 p-6 glass-panel rounded-2xl">
            <h3 className="font-medium text-text-secondary mb-4 border-b border-border pb-2">Variants</h3>
            <div className="flex flex-col gap-4 items-start">
              <GlassButton variant="primary">Primary Variant</GlassButton>
              <GlassButton variant="secondary">Secondary Variant</GlassButton>
              <GlassButton variant="danger">Danger Variant</GlassButton>
              <GlassButton variant="primary" isLoading>Loading State</GlassButton>
            </div>
          </div>

          {/* Sizing */}
          <div className="space-y-4 p-6 glass-panel rounded-2xl">
            <h3 className="font-medium text-text-secondary mb-4 border-b border-border pb-2">Sizes</h3>
            <div className="flex flex-col gap-4 items-start">
              <GlassButton size="lg">Large Size (h-12)</GlassButton>
              <GlassButton size="md">Medium Target (h-11)</GlassButton>
              <GlassButton size="sm">Small (h-9)</GlassButton>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
