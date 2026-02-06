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
import { Link, useRouter } from "@/lib/navigation";

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
                <Avatar className="h-8 w-8 transition-transform hover:scale-105 ring-2 ring-glass-border hover:ring-neon-border">
                    <AvatarImage src={user.avatar_url} />
                    <AvatarFallback className="bg-card text-xs font-medium text-text-highlight">
                        {initials}
                    </AvatarFallback>
                </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 bg-popover border-glass-border text-foreground backdrop-blur-xl">
                <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                        <p className="text-sm font-medium leading-none text-foreground">{user.first_name || "User"}</p>
                        <p className="text-xs leading-none text-text-subtle">{user.email}</p>
                    </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-glass-border" />
                <DropdownMenuItem asChild>
                    <Link href="/settings/profile" className="cursor-pointer hover:bg-glass-bg focus:bg-glass-bg focus:text-foreground">
                        <User className="mr-2 h-4 w-4" />
                        <span>{t("settings")}</span>
                    </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                    <Link href="/settings/billing" className="cursor-pointer hover:bg-glass-bg focus:bg-glass-bg focus:text-foreground">
                        <CreditCard className="mr-2 h-4 w-4" />
                        <span>{t("billing")}</span>
                    </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-glass-border" />
                <DropdownMenuItem
                    className="cursor-pointer text-error-text hover:text-error-text hover:bg-error-bg focus:bg-error-bg focus:text-error-text"
                    onClick={handleLogout}
                >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>{tAuth("logout")}</span>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
