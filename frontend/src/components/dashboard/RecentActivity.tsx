import { GlassCard } from "@/components/ui/glass-card";
import { useTranslations } from "next-intl";
import { FileText, Clock } from "lucide-react";

// Placeholder type until we have the full Diagram type
interface ActivityItem {
    id: string;
    action: string;
    target: string;
    timestamp: string;
}

export function RecentActivity() {
    const t = useTranslations("dashboard");
    
    // Mock data for now
    const activities: ActivityItem[] = [
        { id: "1", action: "Created diagram", target: "CRM v1", timestamp: "2 hours ago" },
        { id: "2", action: "Exported to", target: "Miro Board A", timestamp: "5 hours ago" },
        { id: "3", action: "Updated", target: "User Schema", timestamp: "1 day ago" },
    ];

    return (
        <GlassCard className="col-span-1 md:col-span-2 lg:col-span-3">
             <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-white">
                    {t("recentActivity" as any) || "Recent Activity"}
                </h3>
            </div>
            <div className="space-y-4">
                {activities.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                        <div className="flex items-center space-x-4">
                            <div className="p-2 rounded-full bg-blue-500/20 text-blue-400">
                                <FileText className="h-4 w-4" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-white">{item.target}</p>
                                <p className="text-xs text-white/50">{item.action}</p>
                            </div>
                        </div>
                        <div className="flex items-center text-xs text-white/40">
                            <Clock className="mr-1 h-3 w-3" />
                            {item.timestamp}
                        </div>
                    </div>
                ))}
            </div>
        </GlassCard>
    );
}
