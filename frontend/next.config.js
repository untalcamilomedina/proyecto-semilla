/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Temporarily disable ESLint during builds to fix setup issues
    ignoreDuringBuilds: true,
  },
  // Proxy API requests to backend
  async rewrites() {
    // Use Docker service name in container, localhost in development
    const backendUrl = process.env.NODE_ENV === 'production' 
      ? 'http://proyecto_semilla_backend:8000'
      : 'http://localhost:7777';
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;