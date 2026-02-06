import { createNavigation } from 'next-intl/navigation';
import { locales } from '../config';
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales,
  defaultLocale: 'es'
});

export const { Link, redirect, usePathname, useRouter, getPathname } = createNavigation(routing);
