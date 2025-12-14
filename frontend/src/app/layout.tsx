import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Proyecto Semilla",
  description: "Frontend Next.js para Acme SaaS (Django backend).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="antialiased">{children}</body>
    </html>
  );
}
