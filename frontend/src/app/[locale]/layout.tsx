import type { Metadata, Viewport } from "next";
import { getLocale, getMessages, setRequestLocale } from "next-intl/server";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/sonner";
import "@/app/globals.css"; // Adjusted import path since we moved to [locale]

export const metadata: Metadata = {
  title: {
    default: "BlockFlow Platform",
    template: "%s | BlockFlow",
  },
  description: "Marketplace de herramientas para Notion.",
};

export const viewport: Viewport = {
  themeColor: "#ffffff",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export function generateStaticParams() {
  return [{ locale: "en" }, { locale: "es" }];
}

export default async function LocaleLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}>) {
  const { locale } = await params;

  setRequestLocale(locale);

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <Providers locale={locale} messages={messages}>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
