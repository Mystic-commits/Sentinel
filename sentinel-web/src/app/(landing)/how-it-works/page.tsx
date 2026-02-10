import { AnimatedDemo } from '@/components/landing';

export default function HowItWorksPage() {
    return (
        <div className="py-12">
            <div className="max-w-4xl mx-auto px-6 mb-12 text-center">
                <h1 className="text-4xl font-bold text-txt-primary mb-4">How It Works</h1>
                <p className="text-txt-secondary text-lg">
                    See Sentinel's intelligent pipeline in action.
                </p>
            </div>
            <AnimatedDemo />
        </div>
    );
}
