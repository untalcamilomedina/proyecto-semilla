import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';

export default function HomePage() {
  return (
    <main>
      <Navbar />
      <Hero />
      {/* Other sections will go here */}
      <div style={{height: '100vh', background: 'var(--bg-dark)'}}>
        {/* Spacer to demonstrate scroll */}
      </div>
    </main>
  );
}
