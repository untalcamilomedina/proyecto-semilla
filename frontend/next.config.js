/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Recommended: Enable ESLint during builds for better code quality
    ignoreDuringBuilds: false,
  },
};

module.exports = nextConfig;