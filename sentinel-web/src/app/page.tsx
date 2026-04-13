import { Hero, AnimatedDemo, FeatureGrid, InstallSection, Footer } from '@/components/landing';

export default function Home() {
    return (
        <main className="min-h-screen bg-background">
            <Hero />
            <AnimatedDemo />
            <FeatureGrid />
            <InstallSection />
            <Footer />
        </main>
    );
}
