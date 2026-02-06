"use client";

import { BlockFlowLogo } from "@/components/ui/logo";
import { useState } from "react";
import { Link, usePathname } from "@/lib/navigation";
import { useTranslations } from "next-intl";
import {
    LayoutDashboard,
    Users,
    Shield,
    CreditCard,
    Settings,
    Menu,
    X,
    LogOut,
    ScrollText,
    Key,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LanguageSwitcher } from "@/components/ui/language-switcher";

/**
 * Sidebar
 * Premium navigation bar with glassmorphism and backdrop blur.
 * Uses semantic tokens for full light/dark theme support.
 */
export function Sidebar() {
    const t = useTranslations("nav");
    const ta = useTranslations("auth");
    const tc = useTranslations("common");
    const [isOpen, setIsOpen] = useState(false);
    const pathname = usePathname();
    const { user, tenant, logout } = useAuth();

    const navigation = [
        { name: t("dashboard"), href: "/", icon: LayoutDashboard },
        { name: t("members"), href: "/members", icon: Users },
        { name: t("roles"), href: "/roles", icon: Shield },
        { name: t("billing"), href: "/billing", icon: CreditCard },
        { name: t("auditLogs"), href: "/audit-logs", icon: ScrollText },
        { name: t("apiKeys"), href: "/api-keys", icon: Key },
        { name: t("settings"), href: "/settings", icon: Settings },
    ];

    return (
        <>
            {/* Mobile menu button */}
            <button
                type="button"
                aria-label="Toggle menu"
                className="fixed top-5 left-5 z-50 lg:hidden p-2 rounded-xl bg-glass-bg border border-glass-border backdrop-blur-md"
                onClick={() => setIsOpen(!isOpen)}
            >
                {isOpen ? (
                    <X className="h-5 w-5 text-foreground" />
                ) : (
                    <Menu className="h-5 w-5 text-foreground" />
                )}
            </button>

            {/* Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-40 bg-glass-overlay-strong backdrop-blur-sm lg:hidden animate-in fade-in duration-300"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={cn(
                    "fixed inset-y-0 left-0 z-40 w-64 transform transition-all duration-500 ease-in-out border-r border-glass-border-subtle",
                    "bg-sidebar backdrop-blur-2xl lg:translate-x-0",
                    isOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="flex h-full flex-col">

                    {/* Logo Section */}
                    <div className="flex h-20 shrink-0 items-center gap-3 px-6 border-b border-glass-border-subtle relative overflow-hidden">
                        {/* Soft Glow behind logo (dark only) */}
                        <div className="absolute -top-10 -left-10 w-32 h-32 bg-neon-bg rounded-full blur-3xl hidden dark:block" />

                        <BlockFlowLogo className="h-8 w-8 text-neon z-10" />

                        <span className="text-xl font-bold text-gradient-heading-r truncate z-10">
                            BlockFlow
                        </span>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 space-y-1.5 px-3 py-6 overflow-y-auto custom-scrollbar">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setIsOpen(false)}
                                    className={cn(
                                        "group flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-300",
                                        isActive
                                            ? "bg-neon-bg text-neon-text border border-neon-border shadow-neon"
                                            : "text-text-secondary hover:bg-glass-bg hover:text-foreground border border-transparent"
                                    )}
                                >
                                    <item.icon
                                        className={cn(
                                            "h-5 w-5 shrink-0 transition-transform duration-300 group-hover:scale-110",
                                            isActive ? "text-neon-text" : "text-text-quaternary group-hover:text-text-subtle"
                                        )}
                                    />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User Profile Section */}
                    <div className="border-t border-glass-border-subtle p-4 bg-glass-bg space-y-4">
                        <div className="flex items-center gap-3 px-2">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-neon-bg-strong to-blue-500/20 border border-glass-border flex items-center justify-center relative overflow-hidden">
                                <span className="text-sm font-bold text-neon-text relative z-10">
                                    {(user?.first_name || user?.username || "U").charAt(0).toUpperCase()}
                                </span>
                                <div className="absolute inset-0 bg-neon-bg animate-pulse" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-text-highlight truncate">
                                    {user?.first_name || user?.username || tc("user")}
                                </p>
                                <p className="text-[10px] text-text-tertiary truncate tracking-tight">{user?.email}</p>
                            </div>
                        </div>

                        <div className="flex items-center justify-between gap-2 px-1">
                            <ThemeToggle />
                            <LanguageSwitcher />
                        </div>

                        <GlassButton
                            variant="secondary"
                            className="w-full justify-start py-2.5 text-xs border-transparent hover:border-error-border hover:bg-error-bg hover:text-error-text group"
                            onClick={logout}
                        >
                            <LogOut className="mr-2 h-3.5 w-3.5 opacity-50 group-hover:opacity-100 transition-opacity" />
                            {ta("logout")}
                        </GlassButton>
                    </div>
                </div>
            </aside>
        </>
    );
}
