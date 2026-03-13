/**
 * Feature card component for MDX content.
 * Glass-morphism styled card for showcasing features or products.
 *
 * Usage in MDX:
 * <FeatureCard icon="🚀" title="Fast" description="Lightning fast performance" />
 */
'use client';

interface FeatureCardProps {
  icon?: string;
  title: string;
  description: string;
  href?: string;
}

export function FeatureCard({ icon, title, description, href }: FeatureCardProps) {
  const content = (
    <div className="glass-card p-6 h-full flex flex-col items-start gap-3 group">
      {icon && (
        <span className="text-3xl" aria-hidden="true">{icon}</span>
      )}
      <h3 className="text-lg font-semibold text-white/90 group-hover:text-sky-400 transition-colors">
        {title}
      </h3>
      <p className="text-sm text-white/60 leading-relaxed">{description}</p>
    </div>
  );

  if (href) {
    return (
      <a href={href} className="block no-underline" target={href.startsWith('http') ? '_blank' : undefined}>
        {content}
      </a>
    );
  }

  return content;
}
