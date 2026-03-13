/**
 * Tabbed code block component for MDX content.
 * Shows multiple code snippets in a tabbed interface.
 *
 * Usage in MDX:
 * <CodeTabs tabs={[
 *   { label: "Python", language: "python", code: "print('hello')" },
 *   { label: "JavaScript", language: "js", code: "console.log('hello')" },
 * ]} />
 */
'use client';

import { useState } from 'react';

interface Tab {
  label: string;
  language?: string;
  code: string;
}

interface CodeTabsProps {
  tabs: Tab[];
}

export function CodeTabs({ tabs }: CodeTabsProps) {
  const [activeIndex, setActiveIndex] = useState(0);

  if (!tabs || tabs.length === 0) return null;

  return (
    <div className="my-6 rounded-xl border border-white/10 overflow-hidden">
      {/* Tab headers */}
      <div
        className="flex border-b border-white/10 bg-white/5"
        role="tablist"
        aria-label="Code examples"
      >
        {tabs.map((tab, idx) => (
          <button
            key={tab.label}
            role="tab"
            aria-selected={activeIndex === idx}
            aria-controls={`code-panel-${idx}`}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeIndex === idx
                ? 'text-sky-400 border-b-2 border-sky-400 bg-white/5'
                : 'text-white/50 hover:text-white/70'
            }`}
            onClick={() => setActiveIndex(idx)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Code panel */}
      <div
        id={`code-panel-${activeIndex}`}
        role="tabpanel"
        className="p-4 bg-black/30 overflow-x-auto"
      >
        <pre className="text-sm font-mono text-white/80 whitespace-pre-wrap">
          <code>{tabs[activeIndex].code}</code>
        </pre>
      </div>
    </div>
  );
}
