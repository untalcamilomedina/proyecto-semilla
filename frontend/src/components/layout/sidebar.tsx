"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
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

/**
 * Sidebar
 * Premium navigation bar with glassmorphism and backdrop blur.
 * 
 * @vibe Elite - Integrated with i18n and neon themes.
 */
export function Sidebar() {
    const t = useTranslations("nav");
    const ta = useTranslations("auth");
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
                className="fixed top-5 left-5 z-50 lg:hidden p-2 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md"
                onClick={() => setIsOpen(!isOpen)}
            >
                {isOpen ? (
                    <X className="h-5 w-5 text-white" />
                ) : (
                    <Menu className="h-5 w-5 text-white" />
                )}
            </button>

            {/* Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden animate-in fade-in duration-300"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={cn(
                    "fixed inset-y-0 left-0 z-40 w-64 transform transition-all duration-500 ease-in-out border-r border-white/5",
                    "bg-black/20 backdrop-blur-2xl lg:translate-x-0",
                    isOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="flex h-full flex-col">
                    {/* Logo Section */}
                    <div className="flex h-20 shrink-0 items-center px-6 border-b border-white/5 relative overflow-hidden">
                        {/* Soft Glow behind logo */}
                        <div className="absolute -top-10 -left-10 w-32 h-32 bg-neon/10 rounded-full blur-3xl" />
                        
                        <span className="text-xl font-bold bg-gradient-to-r from-neon to-emerald-400 bg-clip-text text-transparent truncate z-10">
                            {tenant?.name || "Semilla OS"}
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
                                            ? "bg-neon/10 text-neon border border-neon/20 shadow-[0_0_15px_rgba(13,242,13,0.05)]"
                                            : "text-white/50 hover:bg-white/5 hover:text-white border border-transparent"
                                    )}
                                >
                                    <item.icon
                                        className={cn(
                                            "h-5 w-5 shrink-0 transition-transform duration-300 group-hover:scale-110",
                                            isActive ? "text-neon" : "text-white/30 group-hover:text-white/60"
                                        )}
                                    />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User Profile Section */}
                    <div className="border-t border-white/5 p-4 bg-white/[0.02]">
                        <div className="flex items-center gap-3 px-2 mb-4">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-neon/20 to-blue-500/20 border border-white/10 flex items-center justify-center relative overflow-hidden">
                                <span className="text-sm font-bold text-neon relative z-10">
                                    {(user?.first_name || user?.username || "U").charAt(0).toUpperCase()}
                                </span>
                                <div className="absolute inset-0 bg-neon/5 animate-pulse" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-white/90 truncate">
                                    {user?.first_name || user?.username || "Usuario"}
                                </p>
                                <p className="text-[10px] text-white/40 truncate tracking-tight">{user?.email}</p>
                            </div>
                        </div>
                        
                        <GlassButton
                            variant="secondary"
                            className="w-full justify-start py-2.5 text-xs border-transparent hover:border-red-500/30 hover:bg-red-500/5 hover:text-red-400 group"
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
