import type { MetadataRoute } from 'next';
import { publicPages, siteUrl } from '@/lib/site';

export default function sitemap(): MetadataRoute.Sitemap {
    return Object.keys(publicPages).map(path => ({ url: new URL(path, siteUrl).href }));
}
