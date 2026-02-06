import type { Metadata } from "next";

export const metadata: Metadata = {
    title: {
        default: "Autenticación",
        template: "%s | Autenticación",
    },
    description: "Accede a tu cuenta en Proyecto Semilla. Autenticación segura y rápida.",
};

export default function AuthFlowLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <section className="min-h-screen">{children}</section>;
}
