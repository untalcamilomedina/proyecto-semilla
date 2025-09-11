/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7777',
  },
  // Remove standalone output - causes static file issues
  // output: 'standalone',
  // Disable static optimization for pages that require authentication
  experimental: {
    serverComponentsExternalPackages: [],
    forceSwcTransforms: true,
  },
  // Disable image optimization to avoid SSR issues
  images: {
    unoptimized: true,
  },
  // Disable static generation for all pages
  trailingSlash: false,
  // Disable static generation for dashboard pages
  generateBuildId: async () => {
    return 'build-' + Date.now()
  },
  // Disable prerendering for all pages
  generateEtags: false,
  poweredByHeader: false,
  // Disable static generation completely
  staticPageGenerationTimeout: 0,
  // Disable static optimization
  optimizeFonts: false,
  swcMinify: false,
  // Disable all optimizations that might cause SSR issues
  compiler: {
    removeConsole: false,
  },
  // Disable webpack optimizations
  webpack: (config, { dev }) => {
    if (!dev) {
      config.optimization = {
        ...config.optimization,
        minimize: false,
        splitChunks: false,
      };
    }
    return config;
  },
  // Disable rewrites to avoid conflicts with direct API calls
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7777'}/api/:path*`,
  //     },
  //   ];
  // },
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;