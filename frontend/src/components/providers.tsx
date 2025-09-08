'use client';

import { QueryProvider } from '../lib/query-provider';

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryProvider>
      {children}
    </QueryProvider>
  );
}