'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/stores/auth-store';

export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { initialize, isLoading } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Evita llamar a initialize multiples veces en Strict Mode
    if (!isInitialized) {
      initialize().finally(() => {
        setIsInitialized(true);
      });
    }
  }, [initialize, isInitialized]);

  if (isLoading && isInitialized === false) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando sesión...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}