import { ReactNode } from 'react';

// Root layout delegates locale-specific rendering to [locale]/layout.tsx
// The lang attribute is set dynamically based on the active locale
export default function RootLayout({ children }: { children: ReactNode }) {
  return children;
}
