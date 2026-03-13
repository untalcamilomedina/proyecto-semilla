import {useTranslations} from 'next-intl';

export default function About() {
  const t = useTranslations('About');
  
  return (
    <section id="about" className="py-20 relative">
      <div className="container">
        <div className="glass-card max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl font-bold mb-2 text-gradient">{t('title')}</h2>
          <h3 className="text-xl mb-6 text-white/80">{t('subtitle')}</h3>
          <p className="text-lg leading-relaxed text-gray-300">
            {t('description')}
          </p>
        </div>
      </div>
    </section>
  );
}
