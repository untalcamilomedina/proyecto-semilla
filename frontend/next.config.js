/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Temporarily disable ESLint during builds to fix setup issues
    ignoreDuringBuilds: true,
  },
  // Proxy API requests to backend in development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:7777/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;