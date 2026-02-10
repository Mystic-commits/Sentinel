import { Hero, FeatureGrid, AnimatedDemo } from '@/components/landing';
import Link from 'next/link';

export default function Home() {
    return (
        <>
            <Hero />

            {/* Brief Teasers */}
            <div className="py-20 text-center">
                <p className="text-txt-secondary mb-8">
                    Sentinel organizes your files locally using advanced AI.
                </p>
                <div className="flex items-center justify-center gap-4">
                    <Link
                        href="/how-it-works"
                        className="px-6 py-3 bg-surface-2 text-txt-primary font-semibold rounded-xl hover:bg-surface-3 transition-colors"
                    >
                        See how it works
                    </Link>
                    <Link
                        href="/download"
                        className="px-6 py-3 bg-white text-black font-semibold rounded-xl hover:bg-neutral-200 transition-colors"
                    >
                        Download Now
                    </Link>
                </div>
            </div>

            {/* Tease the demo lightly or leave it for the dedicated page? 
                User said "not in a scrollable pattern on one page". 
                I will remove the full scrollable sections here and rely on the dedicated pages.
            */}
        </>
    );
}
