'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/dashboard/sidebar';
import { Header } from '@/components/dashboard/header';
import { apiClient } from '@/lib/api-client';
import { User, Tenant } from '@/types/api';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          router.push('/');
          return;
        }

        // Get current user info from token or API
        // For now, we'll use a placeholder
        setUser({
          id: '1',
          tenant_id: '1',
          email: 'admin@demo-company.com',
          first_name: 'Admin',
          last_name: 'User',
          is_active: true,
          role_id: '1',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });

        setTenant({
          id: '1',
          name: 'Demo Company',
          slug: 'demo-company',
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        });
      } catch (error) {
        console.error('Auth check failed:', error);
        router.push('/');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Cargando...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header user={user} tenant={tenant || undefined} />
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}