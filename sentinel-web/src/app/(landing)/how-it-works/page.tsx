import { pageMetadata } from '@/lib/site';
import { AnimatedDemo } from '@/components/landing';

export default function HowItWorksPage() {
    return (
        <div className="py-12">

            <AnimatedDemo />
        </div>
    );
}

export const metadata = pageMetadata('/how-it-works');
