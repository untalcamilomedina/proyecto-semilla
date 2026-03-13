/**
 * Dynamic MDX renderer component.
 * Takes raw MDX source from the API and renders it with custom components.
 *
 * Uses @mdx-js/mdx for runtime compilation (server-side only).
 */

import { compile, run } from '@mdx-js/mdx';
import * as runtime from 'react/jsx-runtime';
import remarkGfm from 'remark-gfm';
import { useMDXComponents } from '../../../mdx-components';
import { Callout, VideoPlayer, CodeTabs, StepGuide, FeatureCard } from '@/components/mdx';

interface MdxRendererProps {
  /** Raw MDX source content from the API */
  source: string;
}

/**
 * Server Component that compiles and renders MDX content at runtime.
 *
 * This component:
 * 1. Compiles MDX source → JavaScript
 * 2. Runs the compiled code with React runtime
 * 3. Renders with global MDX components + custom components
 */
export async function MdxRenderer({ source }: MdxRendererProps) {
  if (!source) {
    return (
      <div className="text-white/40 italic text-center py-8">
        No content available.
      </div>
    );
  }

  try {
    // Compile MDX source to JavaScript
    const compiled = await compile(source, {
      outputFormat: 'function-body',
      remarkPlugins: [remarkGfm],
    });

    // Run compiled code with React runtime
    const { default: MdxContent } = await run(String(compiled), {
      ...runtime,
      baseUrl: import.meta.url,
    });

    // Get global MDX component overrides
    const components = useMDXComponents({
      // Inject custom interactive components
      Callout,
      VideoPlayer,
      CodeTabs,
      StepGuide,
      FeatureCard,
    });

    return (
      <article className="prose-dark max-w-none">
        <MdxContent components={components} />
      </article>
    );
  } catch (error) {
    console.error('MDX render error:', error);
    return (
      <div className="glass-card p-4 border-l-4 border-red-400">
        <p className="text-red-400 font-semibold">Failed to render content</p>
        <p className="text-white/50 text-sm">
          {error instanceof Error ? error.message : 'Unknown error'}
        </p>
      </div>
    );
  }
}
