import { Hero, ConnectCTA, FAQSection } from '@/components/landing';

export default function Home() {
    return (
        <>
            <Hero />

            <section className="max-w-5xl mx-auto px-6 py-16">
                <p className="text-sm text-amber-400 mb-4">Developer preview · production release in progress</p>
                <h2 className="text-3xl font-semibold mb-8">Your workspace. Your rules.</h2>
                <div className="grid gap-6 md:grid-cols-2">
                    <article className="border border-edge rounded-xl p-6"><h3 className="text-xl mb-3">For individuals</h3><p>Review a local organization plan, select the changes you want, and keep file analysis on your device.</p></article>
                    <article className="border border-edge rounded-xl p-6"><h3 className="text-xl mb-3">For business teams</h3><p>The planned team edition adds shared organization policies, managed devices, and audit controls. Business administration is under development.</p></article>
                </div>
            </section>

            <FAQSection />

            <ConnectCTA />
        </>
    );
}
