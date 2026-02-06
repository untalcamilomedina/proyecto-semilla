import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://blockflow.app'

    return {
        rules: {
            userAgent: '*',
            allow: ['/', '/login', '/signup'],
            disallow: [
                '/dashboard/',
                '/onboarding/',
                '/api/',
                '/_next/',
                '/static/'
            ],
        },
        sitemap: `${baseUrl}/sitemap.xml`,
    }
}
