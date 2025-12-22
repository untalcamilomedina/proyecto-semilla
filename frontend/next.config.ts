import type { NextConfig } from "next";
import withPWA from "@ducanh2912/next-pwa";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n.ts");

const nextConfig: NextConfig = {
  async rewrites() {
    const backend = process.env.DJANGO_BASE_URL || "http://localhost:7777";
    return [
      { source: "/api", destination: `${backend}/api` },
      { source: "/api/:path*", destination: `${backend}/api/:path*` },
    ];
  },
};

export default withPWA({
  dest: "public",
  disable: process.env.NODE_ENV === "development",
  register: true,
  scope: "/",
  sw: "service-worker.js",
})(withNextIntl(nextConfig));
