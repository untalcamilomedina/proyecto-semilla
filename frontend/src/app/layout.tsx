import type { Metadata, Viewport } from "next";
import { getLocale, getMessages } from "next-intl/server";
import { Outfit, Inter } from "next/font/google";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Momentum TIC | Inteligencia en Movimiento",
    template: "%s | Momentum TIC",
  },
  description: "Agentes de IA conversacional para empresas. Automatización inteligente con texto y voz.",
  keywords: ["IA", "Agentes", "Conversacional", "Momentum", "Empresas", "Chatbots"],
  authors: [{ name: "Momentum Team" }],
  creator: "Momentum Team",
  metadataBase: new URL("https://momentumtic.com"),
  openGraph: {
    type: "website",
    locale: "es_MX",
    url: "https://momentumtic.com",
    title: "Momentum TIC - Inteligencia en Movimiento",
    description: "Diseñamos agentes de IA que interactúan de forma natural mediante texto y voz.",
    siteName: "Momentum TIC",
  },
  twitter: {
    card: "summary_large_image",
    title: "Momentum TIC",
    description: "Agentes de IA conversacional para empresas",
    creator: "@momentumtic",
  },
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Momentum",
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

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-heading",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});


export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning>
      <body className={`${outfit.variable} ${inter.variable} antialiased`}>
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
              "name": "Momentum Platform",
              "operatingSystem": "Web",
              "applicationCategory": "BusinessApplication",
              "description": "AI Agents Platform for Business.",
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
              },
              "author": {
                "@type": "Organization",
                "name": "Momentum Team",
                "url": "https://momentumtic.com"
              }
            })
          }}
        />
      </body>
    </html>
  );
}
