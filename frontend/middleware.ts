import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n';

export default createMiddleware({
    locales,
    defaultLocale,
    localeDetection: true,
    localePrefix: 'as-needed',
});

export const config = {
    // Match all pathnames except for API routes, static files, etc.
    matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};
