import { pageMetadata } from '@/lib/site';
import { DocsSection } from '@/components/landing';

export default function DocsPage() {
    return (
        <div className="py-12">

            <DocsSection />
        </div>
    );
}

export const metadata = pageMetadata('/docs');
