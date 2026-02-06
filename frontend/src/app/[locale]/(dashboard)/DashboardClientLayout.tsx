"use client";

import { useEffect } from "react";
import { useRouter } from "@/lib/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Sidebar } from "@/components/layout/sidebar";

/**
 * DashboardClientLayout
 * Main wrapper for the authenticated area.
 * Uses semantic tokens for full light/dark theme support.
 */
export default function DashboardClientLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { isAuthenticated, isLoading, checkAuth } = useAuth();
    const router = useRouter();

    useEffect(() => {
        checkAuth();
    }, [checkAuth]);

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push("/login");
        }
    }, [isLoading, isAuthenticated, router]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-neon" />
            </div>
        );
    }

    if (!isAuthenticated) {
        return null;
    }

    return (
        <div className="min-h-screen bg-background text-foreground relative overflow-hidden">
            {/* Ambient Background Glows (dark mode only) */}
            <div className="fixed inset-0 pointer-events-none hidden dark:block">
                <div className="absolute top-[-10%] left-[-5%] w-[600px] h-[600px] bg-neon-bg rounded-full blur-[120px] opacity-40" />
                <div className="absolute bottom-[-10%] right-[-5%] w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[120px] opacity-40" />
            </div>

            <div className="relative z-10">
                <Sidebar />
                <div className="lg:pl-64 transition-all duration-300">
                    <main className="py-8 px-4 sm:px-6 lg:px-10 max-w-7xl mx-auto">
                        {children}
                    </main>
                </div>
            </div>
        </div>
    );
}
