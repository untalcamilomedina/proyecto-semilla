"use client";

import { NextIntlClientProvider } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { persistQueryClient } from "@tanstack/react-query-persist-client";
import { dexiePersister } from "@/lib/persister";
import { useState, useEffect, type ReactNode } from "react";

interface ProvidersProps {
    children: ReactNode;
    locale: string;
    messages: Record<string, unknown>;
}

export function Providers({ children, locale, messages }: ProvidersProps) {
    const [queryClient] = useState(
        () =>
            new QueryClient({
                defaultOptions: {
                    queries: {
                        staleTime: 60 * 1000, // 1 minute
                        retry: 1,
                        refetchOnWindowFocus: false,
                    },
                },
            })
    );

    useEffect(() => {
        const unsubscribe = persistQueryClient({
            queryClient,
            persister: dexiePersister,
            maxAge: 1000 * 60 * 60 * 24, // 24 hours
        });
        return unsubscribe;
    }, [queryClient]);

    return (
        <NextIntlClientProvider locale={locale} messages={messages}>
            <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
        </NextIntlClientProvider>
    );
}
