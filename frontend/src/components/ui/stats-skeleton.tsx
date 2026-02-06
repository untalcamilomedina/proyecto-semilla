import { Skeleton } from "./skeleton";
import { GlassCard } from "@/components/ui/glass/GlassCard";

interface StatsSkeletonProps {
    count?: number;
}

export function StatsSkeleton({ count = 4 }: StatsSkeletonProps) {
    return (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: count }).map((_, i) => (
                <GlassCard key={i} className="p-6">
                    <div className="flex items-center gap-4">
                        <Skeleton className="h-12 w-12 rounded-2xl" />
                        <div className="space-y-2 flex-1">
                            <Skeleton className="h-3 w-16" />
                            <Skeleton className="h-6 w-12" />
                        </div>
                    </div>
                </GlassCard>
            ))}
        </div>
    );
}
