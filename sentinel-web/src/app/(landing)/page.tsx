import { pageMetadata } from '@/lib/site';
import { Hero, ConnectCTA, FAQSection } from '@/components/landing';

export default function Home() {
    return (
        <>
            <Hero />


            <FAQSection />

            <ConnectCTA />
        </>
    );
}

export const metadata = pageMetadata('/');
