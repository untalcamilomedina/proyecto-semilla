"use client";

import { useTranslations } from "next-intl";
import { User, Lock, Bell } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function SettingsPage() {
    const t = useTranslations("settings");
    const { user } = useAuth();

    return (
        <div className="container max-w-4xl py-10 space-y-8">
             <div>
                <h1 className="text-3xl font-bold text-foreground">{t("title")}</h1>
                <p className="text-text-subtle">{t("description")}</p>
            </div>

            <Tabs defaultValue="profile" className="w-full">
                <TabsList className="bg-glass-bg border border-glass-border p-1">
                    <TabsTrigger value="profile" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-300">
                        <User className="w-4 h-4 mr-2"/> {t("profile")}
                    </TabsTrigger>
                    <TabsTrigger value="security" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-300">
                        <Lock className="w-4 h-4 mr-2"/> {t("security")}
                    </TabsTrigger>
                     <TabsTrigger value="notifications" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-300">
                        <Bell className="w-4 h-4 mr-2"/> {t("notifications")}
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="profile" className="mt-6">
                    <GlassCard className="space-y-6">
                        <div className="space-y-4">
                            <h2 className="text-xl font-bold text-foreground">{t("personalInfo")}</h2>
                            <div className="grid gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="email" className="text-foreground">{t("email")}</Label>
                                    <Input id="email" value={user?.email || ""} disabled className="bg-glass-bg border-glass-border text-text-secondary" />
                                    <p className="text-xs text-text-tertiary">{t("emailCannotChange")}</p>
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="name" className="text-foreground">{t("fullName")}</Label>
                                    <Input id="name" defaultValue={user?.first_name || ""} className="bg-glass-bg border-glass-border text-foreground" />
                                </div>
                            </div>
                        </div>
                        <div className="pt-4 border-t border-glass-border flex justify-end">
                            <Button className="bg-purple-500 hover:bg-purple-600">{t("saveChanges")}</Button>
                        </div>
                    </GlassCard>
                </TabsContent>

                <TabsContent value="security" className="mt-6">
                    <GlassCard className="space-y-6">
                        <div className="space-y-4">
                            <h2 className="text-xl font-bold text-foreground">{t("changePassword")}</h2>
                            <div className="grid gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="current" className="text-foreground">{t("currentPassword")}</Label>
                                    <Input id="current" type="password" className="bg-glass-bg border-glass-border text-foreground" />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="new" className="text-foreground">{t("newPassword")}</Label>
                                    <Input id="new" type="password" className="bg-glass-bg border-glass-border text-foreground" />
                                </div>
                            </div>
                        </div>
                        <div className="pt-4 border-t border-glass-border flex justify-end">
                             <Button className="bg-purple-500 hover:bg-purple-600">{t("updatePassword")}</Button>
                        </div>
                    </GlassCard>
                </TabsContent>

                 <TabsContent value="notifications" className="mt-6">
                    <GlassCard>
                        <div className="text-center py-8 text-text-secondary">
                            {t("notificationsComingSoon")}
                        </div>
                    </GlassCard>
                </TabsContent>
            </Tabs>
        </div>
    );
}
