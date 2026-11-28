import type { MetadataRoute } from 'next';
import { publicPages, siteUrl } from '@/lib/site';

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
    return Object.keys(publicPages).map(path => ({ url: new URL(path, siteUrl).href }));
}
