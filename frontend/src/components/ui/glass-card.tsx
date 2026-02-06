import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function GlassCard({ children, className, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-glass-border bg-glass-bg p-6 backdrop-blur-md shadow-sm transition-all hover:shadow-md hover:bg-glass-bg-hover",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 z-0 bg-gradient-to-br from-glass-bg-hover to-transparent opacity-50 pointer-events-none" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
