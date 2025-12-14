"use client";

// Skip static generation - requires auth
export const dynamic = "force-dynamic";

import { useAuth } from "@/hooks/use-auth";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Users, Shield, CreditCard, BarChart3 } from "lucide-react";

const stats = [
    { name: "Miembros", value: "—", icon: Users, color: "bg-blue-500" },
    { name: "Roles", value: "—", icon: Shield, color: "bg-purple-500" },
    { name: "Facturación", value: "—", icon: CreditCard, color: "bg-green-500" },
    { name: "Uso", value: "—", icon: BarChart3, color: "bg-orange-500" },
];

export default function DashboardPage() {
    const { tenant, user } = useAuth();

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-zinc-900">Dashboard</h1>
                <p className="mt-1 text-sm text-zinc-500">
                    Bienvenido, {user?.first_name || user?.username || "Usuario"}
                </p>
            </div>

            {/* Tenant Info */}
            {tenant && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Organización</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                            <div>
                                <dt className="text-xs font-medium text-zinc-500">Nombre</dt>
                                <dd className="mt-1 text-sm font-semibold text-zinc-900">
                                    {tenant.name}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-xs font-medium text-zinc-500">Slug</dt>
                                <dd className="mt-1 text-sm font-mono text-zinc-700">
                                    {tenant.slug}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-xs font-medium text-zinc-500">Plan</dt>
                                <dd className="mt-1 text-sm font-semibold text-zinc-900">
                                    {tenant.plan_code || "Free"}
                                </dd>
                            </div>
                            <div>
                                <dt className="text-xs font-medium text-zinc-500">Módulos</dt>
                                <dd className="mt-1 text-sm text-zinc-700">
                                    {tenant.enabled_modules?.length || 0} activos
                                </dd>
                            </div>
                        </dl>
                    </CardContent>
                </Card>
            )}

            {/* Stats Grid */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {stats.map((stat) => (
                    <Card key={stat.name}>
                        <CardContent className="p-6">
                            <div className="flex items-center gap-4">
                                <div
                                    className={`flex h-12 w-12 items-center justify-center rounded-lg ${stat.color}`}
                                >
                                    <stat.icon className="h-6 w-6 text-white" />
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-zinc-500">{stat.name}</p>
                                    <p className="text-2xl font-bold text-zinc-900">{stat.value}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Quick Actions */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Acciones rápidas</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        <a
                            href="/members"
                            className="flex items-center gap-3 rounded-lg border border-zinc-200 p-4 hover:bg-zinc-50 transition-colors"
                        >
                            <Users className="h-5 w-5 text-zinc-400" />
                            <span className="font-medium text-zinc-700">Invitar miembros</span>
                        </a>
                        <a
                            href="/roles"
                            className="flex items-center gap-3 rounded-lg border border-zinc-200 p-4 hover:bg-zinc-50 transition-colors"
                        >
                            <Shield className="h-5 w-5 text-zinc-400" />
                            <span className="font-medium text-zinc-700">Gestionar roles</span>
                        </a>
                        <a
                            href="/billing"
                            className="flex items-center gap-3 rounded-lg border border-zinc-200 p-4 hover:bg-zinc-50 transition-colors"
                        >
                            <CreditCard className="h-5 w-5 text-zinc-400" />
                            <span className="font-medium text-zinc-700">Ver facturación</span>
                        </a>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
