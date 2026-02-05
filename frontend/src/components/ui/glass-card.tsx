import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function GlassCard({ children, className, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-white/20 bg-white/10 p-6 backdrop-blur-md shadow-sm transition-all hover:shadow-md hover:bg-white/20 dark:border-white/10 dark:bg-black/10 dark:hover:bg-black/20",
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 z-0 bg-gradient-to-br from-white/10 to-transparent opacity-50 pointer-events-none" />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
