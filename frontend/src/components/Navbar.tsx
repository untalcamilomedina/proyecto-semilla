import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/routing';
import LanguageSwitcher from './LanguageSwitcher';

export default function Navbar() {
  const t = useTranslations('Navigation');
  
  return (
    <nav className="glossy-nav">
      <div className="container" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <Link href="/" className="logo" style={{fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.05em'}}>
          MOMENTUM<span style={{color: 'var(--primary-color)'}}>TIC</span>
        </Link>
        
        <div style={{display: 'flex', gap: '2rem', alignItems: 'center'}} className="nav-links">
          <Link href="/#about">{t('about')}</Link>
          <Link href="/#services">{t('services')}</Link>
          <Link href="/#pricing">{t('pricing')}</Link>
          <LanguageSwitcher />
          <Link href="/#contact" className="btn btn-primary">
            {t('contact')}
          </Link>
        </div>
      </div>
    </nav>
  );
}
