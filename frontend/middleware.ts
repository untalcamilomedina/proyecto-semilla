import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { locales, defaultLocale } from './src/config';

const intlMiddleware = createMiddleware({
    locales,
    defaultLocale,
    localeDetection: true,
    localePrefix: 'as-needed',
});

export default function middleware(request: NextRequest) {
    // 1. Check if user is authenticated (simple cookie check for redirects)
    const isAuth = request.cookies.has("sessionid") || request.cookies.has("csrftoken"); // Rough check, ideal is verified server-side or via specific auth cookie if available
    const { pathname } = request.nextUrl;

    // 2. Redirect root '/' to '/dashboard' if logged in
    // Note: next-intl handles the locale prefix, so we check the localized path too
    if (pathname === "/") {
        if (isAuth) {
             const url = request.nextUrl.clone();
             url.pathname = "/dashboard";
             return NextResponse.redirect(url);
        } else {
             const url = request.nextUrl.clone();
             url.pathname = "/es";
             return NextResponse.redirect(url);
        }
    }

    if (pathname === "/es" || pathname === "/en") {
        if (isAuth) {
             const url = request.nextUrl.clone();
             url.pathname = "/dashboard";
             return NextResponse.redirect(url);
        }
    }

    // 3. Continue with i18n middleware
    return intlMiddleware(request);
}

export const config = {
    // Match all pathnames except for API routes, static files, etc.
    matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};
