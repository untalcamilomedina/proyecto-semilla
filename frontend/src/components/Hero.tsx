import {useTranslations} from 'next-intl';
import {Link} from '@/i18n/routing';
import styles from './Hero.module.css';

export default function Hero() {
  const t = useTranslations('Hero');
  
  return (
    <section className={styles.hero} 
      style={{
        backgroundImage: `linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)), url('/hero-bg.png')`
      }}
    >
      <div className={`container ${styles.content}`}>
        <div className="glass-card" style={{display: 'inline-block', padding: '3rem', maxWidth: '900px'}}>
          <h1 className={`text-gradient ${styles.title}`}>
            {t('title')}
          </h1>
          <p className={styles.description}>
            {t('description')}
          </p>
          <Link href="/#contact" className="btn btn-primary" style={{padding: '1rem 2.5rem', fontSize: '1.1rem'}}>
            {t('cta')}
          </Link>
        </div>
      </div>
    </section>
  );
}
