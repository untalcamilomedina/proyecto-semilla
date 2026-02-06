"use client";

import { Link } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import { ArrowRight, Database, Share2, Zap, Shield, Globe } from "lucide-react";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { BlockFlowLogo } from "@/components/ui/logo";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LanguageSwitcher } from "@/components/ui/language-switcher";

export default function LandingPage() {
  const t = useTranslations("landing");

  return (
    <div className="min-h-screen bg-background text-foreground selection:bg-neon/30 overflow-hidden relative">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BlockFlowLogo className="h-10 w-10 md:h-12 md:w-12 text-foreground" />
            <span className="text-xl md:text-2xl font-bold tracking-tight">BlockFlow</span>
          </div>
          <div className="flex items-center gap-2 md:gap-4 ml-auto">
            {/* Theme Toggle (Mobile & Desktop) */}
            <div className="flex items-center gap-2 md:gap-4">
                 <ThemeToggle />
                 <LanguageSwitcher />
                 <Link href="/login">
                    <GlassButton variant="secondary" className="text-text-subtle hover:text-foreground border-transparent bg-transparent hover:bg-glass-bg">{useTranslations('auth')('login')}</GlassButton>
                 </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-neon/5 rounded-full blur-3xl -z-10 animate-pulse" />
        
        <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-glass-bg border border-glass-border mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
                <span className="w-2 h-2 rounded-full bg-neon animate-pulse" />
                <span className="text-xs font-medium text-text-subtle">{t('beta')}</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-gradient-heading animate-in fade-in slide-in-from-bottom-6 duration-700 delay-100">
                {t('title')}<br />
                <span className="text-neon-text">{t('subtitle')}</span>
            </h1>

            <p className="text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
                {t('description')}
            </p>

            <div className="flex items-center justify-center gap-4 pt-4">
                <Link href="/signup">
                    <GlassButton className="h-12 px-8 text-lg bg-neon-bg text-neon-text border-neon-border hover:bg-neon-bg-strong font-bold backdrop-blur-md">
                        {t('startFree')} <ArrowRight className="ml-2 h-5 w-5" />
                    </GlassButton>
                </Link>
            </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 px-6 bg-glass-bg">
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
            {[
                { icon: Database, title: t('features.notionToMiro.title'), desc: t('features.notionToMiro.desc') },
                { icon: Shield, title: t('features.roleAudit.title'), desc: t('features.roleAudit.desc') },
                { icon: Zap, title: t('features.miroToNotion.title'), desc: t('features.miroToNotion.desc') },
            ].map((feature, i) => (
                <div key={i} className="p-8 rounded-3xl bg-glass-bg border border-glass-border-subtle hover:border-neon-border transition-colors group">
                    <feature.icon className="h-10 w-10 text-text-ghost group-hover:text-neon-text transition-colors mb-6" />
                    <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                    <p className="text-text-secondary leading-relaxed">{feature.desc}</p>
                </div>
            ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-glass-border-subtle">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 opacity-50 text-sm">
            <div className="flex items-center gap-2">
                <BlockFlowLogo className="h-6 w-6" />
                <span>{t('footer.rights')}</span>
            </div>
            <div className="flex gap-6">
                <Link href="#" className="hover:text-foreground">{t('footer.privacy')}</Link>
                <Link href="#" className="hover:text-foreground">{t('footer.terms')}</Link>
                <Link href="#" className="hover:text-foreground">{t('footer.twitter')}</Link>
            </div>
        </div>
      </footer>
    </div>
  );
}
