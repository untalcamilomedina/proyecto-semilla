/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Recommended: Enable ESLint during builds for better code quality
    ignoreDuringBuilds: false,
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