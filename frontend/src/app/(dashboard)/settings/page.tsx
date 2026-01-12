"use client";

import { useTranslations } from "next-intl";
import { GlassCard } from "@/components/ui/glass/GlassCard";
import { GlassButton } from "@/components/ui/glass/GlassButton";
import { GlassInput } from "@/components/ui/glass/GlassInput";
import { Settings, User, Globe, Bell, Palette, Save, ShieldCheck, Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { useMutation } from "@tanstack/react-query";
import { userService } from "@/services/user";
import { tenantService } from "@/services/tenant";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useState } from "react";

const profileSchema = z.object({
    first_name: z.string().min(2, "Min 2 chars"),
    last_name: z.string().min(2, "Min 2 chars"),
});

const passwordSchema = z.object({
    current_password: z.string().min(1, "Required"),
    new_password: z.string().min(8, "Min 8 chars"),
    confirm_password: z.string().min(8, "Min 8 chars"),
}).refine(data => data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ["confirm_password"],
});

const tenantSchema = z.object({
    name: z.string().min(3, "Min 3 chars"),
});

/**
 * SettingsPage
 * Premium configuration interface with Glassmorphism and i18n.
 * 
 * @vibe Elite - Clean, organized, and high-performance settings area.
 */
export default function SettingsPage() {
    const t = useTranslations("settings");
    const tc = useTranslations("common");
    const { tenant, user, checkAuth, loadTenant } = useAuth();
    const [activeTab, setActiveTab] = useState("profile");

    // Forms
    const profileForm = useForm({
        resolver: zodResolver(profileSchema),
        values: {
            first_name: user?.first_name || "",
            last_name: user?.last_name || "",
        }
    });

    const passwordForm = useForm({
        resolver: zodResolver(passwordSchema),
        defaultValues: {
            current_password: "",
            new_password: "",
            confirm_password: "",
        }
    });

    const tenantForm = useForm({
        resolver: zodResolver(tenantSchema),
        values: {
            name: tenant?.name || "",
        }
    });

    // Mutations
    const profileMutation = useMutation({
        mutationFn: userService.updateProfile,
        onSuccess: () => {
            toast.success(t("profileUpdated"));
            checkAuth();
        },
        onError: () => toast.error(tc("error"))
    });

    const passwordMutation = useMutation({
        mutationFn: userService.changePassword,
        onSuccess: () => {
            toast.success(t("passwordChanged"));
            passwordForm.reset();
        },
        onError: (err: any) => {
            const detail = err.body?.current_password?.[0] || tc("error");
            toast.error(detail);
        }
    });

    const tenantMutation = useMutation({
        mutationFn: tenantService.updateSettings,
        onSuccess: () => {
            toast.success(t("orgUpdated"));
            loadTenant();
        },
        onError: () => toast.error(tc("error"))
    });

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-2 duration-500">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-2xl bg-neon/10 border border-neon/20">
                        <Settings className="h-6 w-6 text-neon" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white/90">{t("title")}</h1>
                        <p className="text-sm text-white/40">
                            {t("description")}
                        </p>
                    </div>
                </div>
            </div>

            <div className="grid gap-8 lg:grid-cols-3">
                {/* Navigation sidebar */}
                <div className="lg:col-span-1 space-y-4">
                    <GlassCard className="p-2 border-white/5 bg-white/[0.01]">
                        <nav className="space-y-1">
                            {[
                                { id: "profile", name: t("profile"), icon: User },
                                { id: "security", name: t("security"), icon: ShieldCheck },
                                { id: "organization", name: t("organization"), icon: Globe },
                                { id: "notifications", name: t("notifications"), icon: Bell, disabled: true },
                                { id: "theme", name: t("theme"), icon: Palette, disabled: true },
                            ].map((item) => (
                                <button
                                    key={item.id}
                                    onClick={() => !item.disabled && setActiveTab(item.id)}
                                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                                        activeTab === item.id
                                            ? "bg-neon/10 text-neon border border-neon/10"
                                            : item.disabled 
                                                ? "text-white/10 cursor-not-allowed opacity-50"
                                                : "text-white/40 hover:text-white/70 hover:bg-white/5"
                                    }`}
                                >
                                    <item.icon className="h-4 w-4" />
                                    {item.name}
                                </button>
                            ))}
                        </nav>
                    </GlassCard>
                </div>

                {/* Main Content Area */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Profile Form */}
                    {activeTab === "profile" && (
                        <GlassCard className="p-8 space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
                            <form onSubmit={profileForm.handleSubmit(data => profileMutation.mutate(data))} className="space-y-8">
                                <div className="flex items-center justify-between border-b border-white/5 pb-4">
                                    <div className="flex items-center gap-3">
                                        <User className="h-5 w-5 text-neon/60" />
                                        <h2 className="text-lg font-semibold">{t("personalInfo")}</h2>
                                    </div>
                                    <GlassButton 
                                        type="submit" 
                                        disabled={profileMutation.isPending}
                                        className="h-9 px-4 text-xs"
                                    >
                                        {profileMutation.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Save className="mr-2 h-3.5 w-3.5" />}
                                        {t("saveChanges")}
                                    </GlassButton>
                                </div>
                                
                                <div className="grid sm:grid-cols-2 gap-6">
                                    <GlassInput 
                                        label={t("firstName")} 
                                        {...profileForm.register("first_name")}
                                        error={profileForm.formState.errors.first_name?.message as string}
                                    />
                                    <GlassInput 
                                        label={t("lastName")} 
                                        {...profileForm.register("last_name")}
                                        error={profileForm.formState.errors.last_name?.message as string}
                                    />
                                    <div className="sm:col-span-2">
                                        <GlassInput 
                                            label="Email" 
                                            type="email" 
                                            defaultValue={user?.email || ""}
                                            disabled
                                        />
                                    </div>
                                </div>
                            </form>
                        </GlassCard>
                    )}

                    {/* Security Form */}
                    {activeTab === "security" && (
                        <GlassCard className="p-8 space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
                            <form onSubmit={passwordForm.handleSubmit(data => passwordMutation.mutate(data))} className="space-y-8">
                                <div className="flex items-center justify-between border-b border-white/5 pb-4">
                                    <div className="flex items-center gap-3">
                                        <ShieldCheck className="h-5 w-5 text-purple-400" />
                                        <h2 className="text-lg font-semibold">{t("changePassword")}</h2>
                                    </div>
                                    <GlassButton 
                                        type="submit" 
                                        variant="secondary"
                                        disabled={passwordMutation.isPending}
                                        className="h-9 px-4 text-xs"
                                    >
                                        {passwordMutation.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Save className="mr-2 h-3.5 w-3.5" />}
                                        {t("saveChanges")}
                                    </GlassButton>
                                </div>
                                
                                <div className="space-y-6 max-w-md">
                                    <GlassInput 
                                        label={t("currentPassword")} 
                                        type="password"
                                        {...passwordForm.register("current_password")}
                                        error={passwordForm.formState.errors.current_password?.message as string}
                                    />
                                    <GlassInput 
                                        label={t("newPassword")} 
                                        type="password"
                                        {...passwordForm.register("new_password")}
                                        error={passwordForm.formState.errors.new_password?.message as string}
                                    />
                                    <GlassInput 
                                        label={t("confirmNewPassword")} 
                                        type="password"
                                        {...passwordForm.register("confirm_password")}
                                        error={passwordForm.formState.errors.confirm_password?.message as string}
                                    />
                                </div>
                            </form>
                        </GlassCard>
                    )}

                    {/* Organization Section */}
                    {activeTab === "organization" && (
                        <GlassCard className="p-8 space-y-8 animate-in fade-in slide-in-from-right-4 duration-300">
                            <form onSubmit={tenantForm.handleSubmit(data => tenantMutation.mutate(data))} className="space-y-8">
                                <div className="flex items-center justify-between border-b border-white/5 pb-4">
                                    <div className="flex items-center gap-3">
                                        <Globe className="h-5 w-5 text-blue-400" />
                                        <h2 className="text-lg font-semibold">{t("organization")}</h2>
                                    </div>
                                    <GlassButton 
                                        type="submit" 
                                        disabled={tenantMutation.isPending}
                                        className="h-9 px-4 text-xs"
                                    >
                                        {tenantMutation.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Save className="mr-2 h-3.5 w-3.5" />}
                                        {t("saveChanges")}
                                    </GlassButton>
                                </div>
                                
                                <div className="space-y-6">
                                    <GlassInput 
                                        label={t("organization")} 
                                        {...tenantForm.register("name")}
                                        error={tenantForm.formState.errors.name?.message as string}
                                    />
                                    <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/10 text-xs text-blue-200/60 leading-relaxed font-mono">
                                        {t("language")}: <span className="text-blue-400">{tenant?.default_language?.toUpperCase() || "ES"}</span>
                                        <br />
                                        Plan: <span className="text-purple-400">{tenant?.plan_code?.toUpperCase()}</span>
                                    </div>
                                </div>
                            </form>
                        </GlassCard>
                    )}
                </div>
            </div>
        </div>
    );
}
