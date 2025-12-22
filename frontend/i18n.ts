import { getRequestConfig } from 'next-intl/server';
import { cookies, headers } from 'next/headers';

export const locales = ['es', 'en'] as const;
export const defaultLocale = 'es' as const;

export type Locale = (typeof locales)[number];

export default getRequestConfig(async () => {
    // Try to get locale from cookie first, then from Accept-Language header
    const cookieStore = await cookies();
    const headersList = await headers();

    let locale: Locale = defaultLocale;

    // Check cookie
    const localeCookie = cookieStore.get('locale')?.value;
    if (localeCookie && locales.includes(localeCookie as Locale)) {
        locale = localeCookie as Locale;
    } else {
        // Check Accept-Language header
        const acceptLanguage = headersList.get('accept-language');
        if (acceptLanguage) {
            const preferredLocale = acceptLanguage
                .split(',')[0]
                .split('-')[0]
                .toLowerCase();
            if (locales.includes(preferredLocale as Locale)) {
                locale = preferredLocale as Locale;
            }
        }
    }

    return {
        locale,
        messages: (await import(`./messages/${locale}.json`)).default,
    };
});
