import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/routing';

export default function Pricing() {
  const t = useTranslations('Pricing');
  const keys = ['basic', 'standard', 'pro'];
  
  return (
    <section id="pricing" className="py-20">
      <div className="container">
        <h2 className="text-3xl font-bold mb-12 text-center text-gradient">{t('title')}</h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {keys.map((key) => (
            <div key={key} className={`glass-card flex flex-col ${key === 'standard' ? 'border-primary/50 bg-white/10' : ''}`}>
              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-2">{t(`items.${key}.name`)}</h3>
                <div className="text-4xl font-bold text-gradient">{t(`items.${key}.price`)}</div>
              </div>
              
              <ul className="mb-8 flex-grow space-y-3">
                {/* 
                  Since we can't easily iterate arrays in next-intl without rich text or structure,
                  we assume fixed keys or we limit features. 
                  Ideally we'd use t.rich or helper, but for now we map known feature indices if necessary
                  or just use a generic list if the JSON structure allows it.
                  
                  Actually, next-intl returns objects if we ask for `items.${key}.features`.
                */}
                {(t.raw(`items.${key}.features`) as string[]).map((feature, idx) => (
                  <li key={idx} className="flex items-start text-sm text-gray-300">
                    <span className="mr-2 text-green-400">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              
              <Link href="/#contact" className={`btn w-full text-center ${key === 'standard' ? 'btn-primary' : 'bg-white/10 hover:bg-white/20'}`}>
                {t.raw('Navigation.contact') || 'Contact'} 
                {/* Fallback accessing global nav if needed, or just hardcode/add to pricing json */}
                Solicitar
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
