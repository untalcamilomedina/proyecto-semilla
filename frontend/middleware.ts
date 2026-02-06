import createMiddleware from 'next-intl/middleware';
import { NextRequest, NextResponse } from 'next/server';
import { routing } from './src/lib/routing';

const intlMiddleware = createMiddleware(routing);

export default function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Redirect authenticated users from root/locale-root to dashboard
    const isAuth = request.cookies.has("sessionid") || request.cookies.has("csrftoken");
    if (isAuth && (pathname === "/" || /^\/(es|en)\/?$/.test(pathname))) {
        const url = request.nextUrl.clone();
        url.pathname = `/${routing.defaultLocale}/dashboard`;
        return NextResponse.redirect(url);
    }

    return intlMiddleware(request);
}

export const config = {
    matcher: ['/', '/(es|en)/:path*'],
};
