import {useTranslations} from 'next-intl';

export default function Services() {
  const t = useTranslations('Services');
  
  return (
    <section id="services" className="py-20">
      <div className="container">
        <h2 className="text-3xl font-bold mb-12 text-center text-gradient">{t('title')}</h2>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {['agents', 'labs'].map((key) => (
            <div key={key} className="glass-card hover:bg-white/5 transition-all duration-300 group">
              <h3 className="text-2xl font-bold mb-4 text-primary group-hover:text-blue-400">
                {t(`items.${key}.title`)}
              </h3>
              <p className="text-gray-400 leading-relaxed">
                {t(`items.${key}.description`)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
