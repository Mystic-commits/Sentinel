import { pageMetadata } from '@/lib/site';
import { FeatureGrid } from '@/components/landing';

export default function FeaturesPage() {
    return (
        <div className="py-12">

            <FeatureGrid />
        </div>
    );
}

export const metadata = pageMetadata('/features');
