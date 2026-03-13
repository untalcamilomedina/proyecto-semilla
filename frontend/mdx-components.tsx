import type { MDXComponents } from 'mdx/types';

/**
 * Global MDX component overrides.
 * These map standard HTML elements and custom components
 * for use in MDX content rendering.
 */
export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    // Headings with glassmorphism-compatible styling
    h1: ({ children }) => (
      <h1 className="text-4xl font-bold mt-8 mb-4 text-gradient">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="text-3xl font-semibold mt-6 mb-3 text-white/90">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="text-2xl font-medium mt-4 mb-2 text-white/80">{children}</h3>
    ),

    // Paragraph
    p: ({ children }) => (
      <p className="mb-4 leading-relaxed text-white/70">{children}</p>
    ),

    // Links
    a: ({ href, children }) => (
      <a
        href={href}
        className="text-sky-400 hover:text-sky-300 underline decoration-sky-400/30 hover:decoration-sky-300 transition-colors"
        target={href?.startsWith('http') ? '_blank' : undefined}
        rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
      >
        {children}
      </a>
    ),

    // Code blocks
    pre: ({ children }) => (
      <pre className="glass-card my-4 p-4 overflow-x-auto text-sm rounded-xl border border-white/10">
        {children}
      </pre>
    ),
    code: ({ children, className }) => {
      const isInline = !className;
      if (isInline) {
        return (
          <code className="bg-white/10 px-1.5 py-0.5 rounded text-sky-300 text-sm font-mono">
            {children}
          </code>
        );
      }
      return <code className={className}>{children}</code>;
    },

    // Blockquote (callout style)
    blockquote: ({ children }) => (
      <blockquote className="glass-card my-4 border-l-4 border-sky-400 pl-4 italic text-white/60">
        {children}
      </blockquote>
    ),

    // Lists
    ul: ({ children }) => (
      <ul className="list-disc list-inside mb-4 space-y-1 text-white/70">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal list-inside mb-4 space-y-1 text-white/70">{children}</ol>
    ),
    li: ({ children }) => <li className="leading-relaxed">{children}</li>,

    // Table (GFM)
    table: ({ children }) => (
      <div className="overflow-x-auto my-4 glass-card p-0 rounded-xl">
        <table className="w-full text-sm">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th className="text-left p-3 border-b border-white/10 font-semibold text-white/90">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="p-3 border-b border-white/5 text-white/70">{children}</td>
    ),

    // Horizontal rule
    hr: () => <hr className="my-8 border-white/10" />,

    // Images
    img: ({ src, alt }) => (
      <figure className="my-6">
        <img
          src={src}
          alt={alt || ''}
          className="rounded-xl w-full object-cover"
          loading="lazy"
        />
        {alt && (
          <figcaption className="text-center text-sm text-white/50 mt-2">{alt}</figcaption>
        )}
      </figure>
    ),

    // Spread any additional custom components
    ...components,
  };
}
