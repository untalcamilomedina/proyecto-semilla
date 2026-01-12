import type { Metadata, Viewport } from "next";
import { getLocale, getMessages } from "next-intl/server";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Proyecto Semilla | SaaS Boilerplate Elite",
    template: "%s | Proyecto Semilla",
  },
  description: "Plataforma SaaS de alto rendimiento impulsada por Django + Next.js con estética Glassmorphism.",
  keywords: ["SaaS", "Boilerplate", "Django", "Next.js", "Enterprise", "PWA"],
  authors: [{ name: "Semilla Team" }],
  creator: "Semilla Team",
  metadataBase: new URL("https://semilla.automacon.com.mx"),
  openGraph: {
    type: "website",
    locale: "es_MX",
    url: "https://semilla.automacon.com.mx",
    title: "Proyecto Semilla - SaaS Boilerplate Elite",
    description: "La base definitiva para tus proyectos SaaS con Django y Next.js.",
    siteName: "Proyecto Semilla",
  },
  twitter: {
    card: "summary_large_image",
    title: "Proyecto Semilla",
    description: "SaaS Boilerplate Elite con Django + Next.js",
    creator: "@semilla_os",
  },
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Semilla",
  },
  formatDetection: {
    telephone: false,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export const viewport: Viewport = {
  themeColor: "#ffffff",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning>
      <body className="antialiased">
        <Providers locale={locale} messages={messages}>
          {children}
          <Toaster />
        </Providers>
        
        {/* GEO Optimization: JSON-LD for SoftwareApplication */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "Proyecto Semilla",
              "operatingSystem": "Web",
              "applicationCategory": "BusinessApplication",
              "description": "SaaS Platform powered by Django + Next.js with Elite Glassmorphism UI.",
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
              },
              "author": {
                "@type": "Organization",
                "name": "Semilla Team",
                "url": "https://semilla.automacon.com.mx"
              }
            })
          }}
        />
      </body>
    </html>
  );
}
