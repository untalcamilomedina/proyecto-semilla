import {useTranslations} from 'next-intl';

export default function Footer() {
  const t = useTranslations('Footer');
  
  return (
    <footer id="contact" className="py-12 border-t border-white/10 bg-black/50 backdrop-blur-lg">
      <div className="container text-center">
        <h2 className="text-2xl font-bold mb-6">MOMENTUM<span className="text-primary">TIC</span></h2>
        
        <a href={`mailto:${t('contact')}`} className="text-xl text-gray-300 hover:text-white transition-colors mb-8 inline-block">
          {t('contact')}
        </a>
        
        <p className="text-sm text-gray-500 mt-8">
          {t('copyright')}
        </p>
      </div>
    </footer>
  );
}
