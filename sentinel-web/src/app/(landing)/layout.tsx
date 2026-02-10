import { Navbar, Footer } from '@/components/landing';

export default function LandingLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-surface-0 flex flex-col">
            <Navbar />
            <main className="flex-1 pt-20">
                {children}
            </main>
            <Footer />
        </div>
    );
}
