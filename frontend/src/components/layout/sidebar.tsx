"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Users,
    Shield,
    CreditCard,
    Settings,
    Menu,
    X,
    LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";

const navigation = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Miembros", href: "/members", icon: Users },
    { name: "Roles", href: "/roles", icon: Shield },
    { name: "Facturación", href: "/billing", icon: CreditCard },
    { name: "Configuración", href: "/settings", icon: Settings },
];

export function Sidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const pathname = usePathname();
    const { user, tenant, logout } = useAuth();

    return (
        <>
            {/* Mobile menu button */}
            <button
                type="button"
                className="fixed top-4 left-4 z-50 lg:hidden"
                onClick={() => setIsOpen(!isOpen)}
            >
                {isOpen ? (
                    <X className="h-6 w-6 text-zinc-700" />
                ) : (
                    <Menu className="h-6 w-6 text-zinc-700" />
                )}
            </button>

            {/* Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/50 lg:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={cn(
                    "fixed inset-y-0 left-0 z-40 w-64 transform bg-white border-r border-zinc-200 transition-transform duration-300 ease-in-out",
                    "lg:translate-x-0 lg:static lg:inset-auto",
                    isOpen ? "translate-x-0" : "-translate-x-full"
                )}
            >
                <div className="flex h-full flex-col">
                    {/* Logo */}
                    <div className="flex h-16 shrink-0 items-center px-6 border-b border-zinc-200">
                        <span className="text-xl font-bold text-indigo-600">
                            {tenant?.name || "Proyecto Semilla"}
                        </span>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 space-y-1 px-3 py-4">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    onClick={() => setIsOpen(false)}
                                    className={cn(
                                        "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                                        isActive
                                            ? "bg-indigo-50 text-indigo-600"
                                            : "text-zinc-700 hover:bg-zinc-50 hover:text-zinc-900"
                                    )}
                                >
                                    <item.icon
                                        className={cn(
                                            "h-5 w-5 shrink-0",
                                            isActive ? "text-indigo-600" : "text-zinc-400 group-hover:text-zinc-500"
                                        )}
                                    />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User section */}
                    <div className="border-t border-zinc-200 p-4">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="h-9 w-9 rounded-full bg-indigo-100 flex items-center justify-center">
                                <span className="text-sm font-medium text-indigo-600">
                                    {user?.email?.charAt(0).toUpperCase() || "U"}
                                </span>
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-zinc-900 truncate">
                                    {user?.first_name || user?.username || "Usuario"}
                                </p>
                                <p className="text-xs text-zinc-500 truncate">{user?.email}</p>
                            </div>
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="w-full justify-start text-zinc-600"
                            onClick={logout}
                        >
                            <LogOut className="mr-2 h-4 w-4" />
                            Cerrar sesión
                        </Button>
                    </div>
                </div>
            </aside>
        </>
    );
}
