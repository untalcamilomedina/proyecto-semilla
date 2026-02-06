"use client";

import { NextIntlClientProvider } from "next-intl";
import { ThemeProvider } from "next-themes";
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
        // persistQueryClient returns [unsubscribe, promise]
        // We only need to return the unsubscribe function for cleanup
        const [unsubscribe] = persistQueryClient({
            queryClient,
            persister: dexiePersister,
            maxAge: 1000 * 60 * 60 * 24, // 24 hours
        }) as unknown as [() => void, Promise<void>];

        return unsubscribe;
    }, [queryClient]);

    return (
        <NextIntlClientProvider locale={locale} messages={messages}>
            <QueryClientProvider client={queryClient}>
                <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
                    {children}
                </ThemeProvider>
            </QueryClientProvider>
        </NextIntlClientProvider>
    );
}
