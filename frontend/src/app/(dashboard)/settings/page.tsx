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
    const t = useTranslations("common"); // Using common for now, assuming settings keys exist
    const { user } = useAuth();

    return (
        <div className="container max-w-4xl py-10 space-y-8">
             <div>
                <h1 className="text-3xl font-bold text-white glow-text">Settings</h1>
                <p className="text-white/60">Manage your account preferences and security.</p>
            </div>

            <Tabs defaultValue="profile" className="w-full">
                <TabsList className="bg-white/5 border border-white/10 p-1">
                    <TabsTrigger value="profile" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-300">
                        <User className="w-4 h-4 mr-2"/> Profile
                    </TabsTrigger>
                    <TabsTrigger value="security" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-300">
                        <Lock className="w-4 h-4 mr-2"/> Security
                    </TabsTrigger>
                     <TabsTrigger value="notifications" className="data-[state=active]:bg-purple-500/20 data-[state=active]:text-purple-300">
                        <Bell className="w-4 h-4 mr-2"/> Notifications
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="profile" className="mt-6">
                    <GlassCard className="space-y-6">
                        <div className="space-y-4">
                            <h2 className="text-xl font-bold text-white">Profile Information</h2>
                            <div className="grid gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="email" className="text-white">Email</Label>
                                    <Input id="email" value={user?.email || ""} disabled className="bg-white/5 border-white/10 text-white/50" />
                                    <p className="text-xs text-white/40">Email cannot be changed.</p>
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="name" className="text-white">Full Name</Label>
                                    <Input id="name" defaultValue={user?.first_name || ""} className="bg-white/5 border-white/10 text-white" />
                                </div>
                            </div>
                        </div>
                        <div className="pt-4 border-t border-white/10 flex justify-end">
                            <Button className="bg-purple-500 hover:bg-purple-600">Save Changes</Button>
                        </div>
                    </GlassCard>
                </TabsContent>

                <TabsContent value="security" className="mt-6">
                    <GlassCard className="space-y-6">
                        <div className="space-y-4">
                            <h2 className="text-xl font-bold text-white">Change Password</h2>
                            <div className="grid gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="current" className="text-white">Current Password</Label>
                                    <Input id="current" type="password" className="bg-white/5 border-white/10 text-white" />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="new" className="text-white">New Password</Label>
                                    <Input id="new" type="password" className="bg-white/5 border-white/10 text-white" />
                                </div>
                            </div>
                        </div>
                        <div className="pt-4 border-t border-white/10 flex justify-end">
                             <Button className="bg-purple-500 hover:bg-purple-600">Update Password</Button>
                        </div>
                    </GlassCard>
                </TabsContent>
                
                 <TabsContent value="notifications" className="mt-6">
                    <GlassCard>
                        <div className="text-center py-8 text-white/50">
                            Notification settings coming soon.
                        </div>
                    </GlassCard>
                </TabsContent>
            </Tabs>
        </div>
    );
}
