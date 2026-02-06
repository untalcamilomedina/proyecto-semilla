"use client";

import { useLocale } from "next-intl";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { Languages } from "lucide-react";
import { usePathname, useRouter } from "@/lib/navigation";

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const toggleLocale = () => {
    const newLocale = locale === "es" ? "en" : "es";
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <GlassButton
      variant="secondary"
      className="h-9 px-3 py-1 text-xs gap-2 border-white/5 hover:bg-white/10 text-white/60 hover:text-white"
      onClick={toggleLocale}
      aria-label="Switch language"
    >
      <Languages className="h-3.5 w-3.5" />
      <span className="font-mono uppercase">{locale}</span>
    </GlassButton>
  );
}
