/**
 * Callout component for MDX content.
 * Renders styled alert boxes matching the glassmorphism design.
 *
 * Usage in MDX:
 * <Callout type="info">Informational note</Callout>
 * <Callout type="warning">Be careful!</Callout>
 * <Callout type="success">All good!</Callout>
 * <Callout type="error">Something went wrong</Callout>
 */
'use client';

import type { ReactNode } from 'react';

interface CalloutProps {
  type?: 'info' | 'warning' | 'success' | 'error';
  title?: string;
  children: ReactNode;
}

const iconMap = {
  info: '💡',
  warning: '⚠️',
  success: '✅',
  error: '❌',
};

const borderColorMap = {
  info: 'border-sky-400',
  warning: 'border-amber-400',
  success: 'border-emerald-400',
  error: 'border-red-400',
};

const bgMap = {
  info: 'bg-sky-400/5',
  warning: 'bg-amber-400/5',
  success: 'bg-emerald-400/5',
  error: 'bg-red-400/5',
};

export function Callout({ type = 'info', title, children }: CalloutProps) {
  return (
    <div
      className={`my-4 rounded-xl border-l-4 p-4 backdrop-blur-md ${borderColorMap[type]} ${bgMap[type]}`}
      role="alert"
      aria-label={title || `${type} callout`}
    >
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0 mt-0.5" aria-hidden="true">
          {iconMap[type]}
        </span>
        <div className="flex-1">
          {title && (
            <p className="font-semibold text-white/90 mb-1">{title}</p>
          )}
          <div className="text-white/70 text-sm leading-relaxed">{children}</div>
        </div>
      </div>
    </div>
  );
}
