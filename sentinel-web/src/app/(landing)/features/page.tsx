import { FeatureGrid } from '@/components/landing';

export default function FeaturesPage() {
    return (
        <div className="py-12">
            <div className="max-w-4xl mx-auto px-6 mb-12 text-center">
                <h1 className="text-4xl font-bold text-txt-primary mb-4">Features</h1>
                <p className="text-txt-secondary text-lg">
                    Capabilities designed for local-first privacy and control.
                </p>
            </div>
            <FeatureGrid />
        </div>
    );
}
