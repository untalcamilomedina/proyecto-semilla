import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
    return {
        rules: {
            userAgent: '*',
            allow: ['/', '/login', '/signup', '/docs'],
            disallow: [
                '/dashboard/',
                '/onboarding/',
                '/api/',
                '/_next/',
                '/static/'
            ],
        },
        sitemap: 'https://semilla.automacon.com.mx/sitemap.xml',
    }
}
