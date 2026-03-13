import {useTranslations} from 'next-intl';

export default function Process() {
  const t = useTranslations('Process');
  const steps = t.raw('steps') as Array<{title: string, desc: string}>;
  
  return (
    <section className="py-20 relative overflow-hidden">
      <div className="container">
        <h2 className="text-3xl font-bold mb-12 text-center text-gradient">{t('title')}</h2>
        
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
          {steps.map((step, idx) => (
            <div key={idx} className="glass-card p-6 border-l-4 border-l-primary/50 hover:border-l-primary transition-colors">
              <h3 className="text-xl font-bold mb-2 text-white">{step.title}</h3>
              <p className="text-sm text-gray-400">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
