import { Navbar, Hero, AnimatedDemo, FeatureGrid, DownloadSection, DocsSection, InstallSection, Footer } from '@/components/landing';

export default function Home() {
    return (
        <main className="min-h-screen bg-surface-0">
            <Navbar />
            <Hero />
            <AnimatedDemo />
            <FeatureGrid />
            <DownloadSection />
            <DocsSection />
            <InstallSection />
            <Footer />
        </main>
    );
}
