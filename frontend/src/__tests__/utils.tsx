import { render, type RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NextIntlClientProvider } from "next-intl";
import type { ReactElement, ReactNode } from "react";

// Minimal messages for tests
import enMessages from "../../messages/en.json";

function createTestQueryClient() {
    return new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                gcTime: 0,
            },
            mutations: {
                retry: false,
            },
        },
    });
}

interface WrapperProps {
    children: ReactNode;
}

function AllProviders({ children }: WrapperProps) {
    const queryClient = createTestQueryClient();

    return (
        <NextIntlClientProvider locale="en" messages={enMessages}>
            <QueryClientProvider client={queryClient}>
                {children}
            </QueryClientProvider>
        </NextIntlClientProvider>
    );
}

function renderWithProviders(
    ui: ReactElement,
    options?: Omit<RenderOptions, "wrapper">
) {
    return render(ui, { wrapper: AllProviders, ...options });
}

export { renderWithProviders, createTestQueryClient };
export { screen, waitFor, within, act } from "@testing-library/react";
export { default as userEvent } from "@testing-library/user-event";
