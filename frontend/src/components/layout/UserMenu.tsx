"use client";

import { useAuth } from "@/hooks/use-auth";
import { useTranslations } from "next-intl";
import { 
    DropdownMenu, 
    DropdownMenuContent, 
    DropdownMenuItem, 
    DropdownMenuLabel, 
    DropdownMenuSeparator, 
    DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { LogOut, User, Settings, CreditCard } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export function UserMenu() {
    const { user, logout } = useAuth();
    const t = useTranslations("nav");
    const tAuth = useTranslations("auth");
    const router = useRouter();

    if (!user) return null;

    const initials = user.email
        .split("@")[0]
        .slice(0, 2)
        .toUpperCase();

    const handleLogout = async () => {
        await logout();
        router.push("/login");
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger className="outline-none">
                <Avatar className="h-8 w-8 transition-transform hover:scale-105 ring-2 ring-white/10 hover:ring-neon/50">
                    <AvatarImage src={user.avatar_url} />
                    <AvatarFallback className="bg-glass-card text-xs font-medium text-white/80">
                        {initials}
                    </AvatarFallback>
                </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-glass-panel border-white/10 text-white backdrop-blur-xl">
                <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                        <p className="text-sm font-medium leading-none text-white">{user.first_name || "User"}</p>
                        <p className="text-xs leading-none text-white/60">{user.email}</p>
                    </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-white/10" />
                <DropdownMenuItem asChild>
                    <Link href="/settings/profile" className="cursor-pointer hover:bg-white/5 focus:bg-white/5 focus:text-white">
                        <User className="mr-2 h-4 w-4" />
                        <span>{t("settings")}</span>
                    </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                    <Link href="/settings/billing" className="cursor-pointer hover:bg-white/5 focus:bg-white/5 focus:text-white">
                        <CreditCard className="mr-2 h-4 w-4" />
                        <span>{t("billing")}</span>
                    </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-white/10" />
                <DropdownMenuItem 
                    className="cursor-pointer text-red-400 hover:text-red-300 hover:bg-red-500/10 focus:bg-red-500/10 focus:text-red-300"
                    onClick={handleLogout}
                >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>{tAuth("logout")}</span>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
