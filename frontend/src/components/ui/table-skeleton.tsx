import { Skeleton } from "./skeleton";

interface TableSkeletonProps {
    rows?: number;
    columns?: number;
}

export function TableSkeleton({ rows = 5, columns = 4 }: TableSkeletonProps) {
    return (
        <div className="space-y-3">
            {/* Header */}
            <div className="flex gap-4 p-4">
                {Array.from({ length: columns }).map((_, i) => (
                    <Skeleton key={`h-${i}`} className="h-4 flex-1" />
                ))}
            </div>
            {/* Rows */}
            {Array.from({ length: rows }).map((_, row) => (
                <div key={`r-${row}`} className="flex gap-4 px-4 py-3">
                    {Array.from({ length: columns }).map((_, col) => (
                        <Skeleton key={`r-${row}-c-${col}`} className="h-4 flex-1" />
                    ))}
                </div>
            ))}
        </div>
    );
}
