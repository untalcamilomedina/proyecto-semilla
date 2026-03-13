import {useTranslations} from 'next-intl';

export default function Team() {
  const t = useTranslations('Team');
  const members = t.raw('members') as Array<{name: string, role: string}>;
  
  return (
    <section className="py-20">
      <div className="container text-center">
        <h2 className="text-3xl font-bold mb-12 text-gradient">{t('title')}</h2>
        
        <div className="flex flex-wrap justify-center gap-8">
          {members.map((member, idx) => (
            <div key={idx} className="glass-card w-64 p-8 flex flex-col items-center">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-secondary mb-4 opacity-80"></div>
              <h3 className="text-xl font-bold">{member.name}</h3>
              <p className="text-primary text-sm">{member.role}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
