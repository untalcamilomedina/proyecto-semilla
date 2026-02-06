import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";

export async function generateMetadata({
    params,
}: {
    params: Promise<{ locale: string }>;
}): Promise<Metadata> {
    const { locale } = await params;
    const t = await getTranslations({ locale, namespace: "auth" });

    return {
        title: {
            default: t("metaTitle"),
            template: `%s | ${t("metaTitle")}`,
        },
        description: t("metaDescription"),
    };
}

export default function AuthFlowLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <section className="min-h-screen">{children}</section>;
}
