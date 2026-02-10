import { DocsSection } from '@/components/landing';

export default function DocsPage() {
    return (
        <div className="py-12">
            <div className="max-w-4xl mx-auto px-6 mb-12 text-center">
                <h1 className="text-4xl font-bold text-txt-primary mb-4">Documentation</h1>
            </div>
            <DocsSection />
        </div>
    );
}
