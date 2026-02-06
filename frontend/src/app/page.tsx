import { redirect } from 'next/navigation';
import { routing } from '@/lib/routing';

export default function RootPage() {
    redirect(`/${routing.defaultLocale}`);
}
