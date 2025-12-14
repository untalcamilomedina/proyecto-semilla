import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    const backend = process.env.DJANGO_BASE_URL || "http://localhost:7777";
    return [
      { source: "/api", destination: `${backend}/api` },
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
    ];
  },
};

export default nextConfig;
