"use client";

import { useReportWebVitals } from "next/web-vitals";

export function WebVitals() {
    useReportWebVitals((metric) => {
        // Log to console in development
        if (process.env.NODE_ENV === "development") {
            console.log(`[Web Vital] ${metric.name}: ${metric.value.toFixed(1)}ms`);
        }

        // Send to analytics endpoint in production
        if (process.env.NODE_ENV === "production" && process.env.NEXT_PUBLIC_ANALYTICS_URL) {
            fetch(process.env.NEXT_PUBLIC_ANALYTICS_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: metric.name,
                    value: metric.value,
                    rating: metric.rating,
                    id: metric.id,
                    navigationType: metric.navigationType,
                }),
            }).catch(() => {});
        }
    });

    return null;
}
