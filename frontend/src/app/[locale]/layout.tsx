import type { Metadata, Viewport } from "next";
import { getLocale, getMessages, getTranslations, setRequestLocale } from "next-intl/server";
import { Providers } from "@/components/providers";
import { WebVitals } from "@/components/web-vitals";
import { Toaster } from "@/components/ui/sonner";
import "@/app/globals.css";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "meta" });

  return {
    title: {
      default: t("title"),
      template: `%s | ${t("siteName")}`,
    },
    description: t("description"),
    metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "https://blockflow.app"),
    openGraph: {
      title: t("title"),
      description: t("description"),
      siteName: t("siteName"),
      locale,
      type: "website",
    },
  };
}

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
    <html lang={locale} suppressHydrationWarning>
      <body>
        <Providers locale={locale} messages={messages}>
          <WebVitals />
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
