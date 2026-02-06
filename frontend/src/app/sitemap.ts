import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'https://blockflow.app'
    const locales = ['en', 'es']

    const routes = ['', '/login', '/signup']

    return locales.flatMap((locale) =>
        routes.map((route) => ({
            url: `${baseUrl}/${locale}${route}`,
            lastModified: new Date(),
            changeFrequency: route === '' ? 'daily' as const : 'monthly' as const,
            priority: route === '' ? 1 : 0.8,
        }))
    )
}
