import createNextIntlPlugin from 'next-intl/plugin';
import createMDX from '@next/mdx';
import remarkGfm from 'remark-gfm';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';

const withNextIntl = createNextIntlPlugin();

const withMDX = createMDX({
  options: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [rehypeSlug, rehypeAutolinkHeadings],
  },
});

// Backend Django al que se proxyean las llamadas /api/* (server-side).
const DJANGO_BASE_URL = process.env.DJANGO_BASE_URL || 'http://localhost:8000';

const securityHeaders = [
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'same-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
];

const nextConfig = {
  pageExtensions: ['js', 'jsx', 'md', 'mdx', 'ts', 'tsx'],
  // Imagen Docker mínima (stage `runner` del Dockerfile).
  output: 'standalone' as const,
  poweredByHeader: false,
  async rewrites() {
    return [
      // Proxy del API al backend: permite llamadas relativas sin CORS en dev.
      { source: '/api/:path*', destination: `${DJANGO_BASE_URL}/api/:path*` },
    ];
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};

export default withNextIntl(withMDX(nextConfig));
