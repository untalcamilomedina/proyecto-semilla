'use client';

import { useState } from 'react';
import { Bell, Search, LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import { useRouter } from 'next/navigation';
import { TenantSwitcher } from './tenant-switcher';

interface HeaderProps {
  user?: {
    first_name?: string | null;
    last_name?: string | null;
    email: string;
  };
}

export function Header({ user }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const router = useRouter();

  const handleLogout = () => {
    apiClient.logout();
    router.push('/');
  };

  const firstName = user?.first_name ?? '';
  const lastName = user?.last_name ?? '';

  const userInitials = (firstName || lastName)
    ? `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
    : 'U';

  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Buscar..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 w-64"
          />
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Tenant Switcher */}
        <TenantSwitcher />

        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            3
          </span>
        </Button>

        {/* User Info */}
        <div className="flex items-center space-x-3">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">
              {(firstName || lastName)
                ? `${firstName} ${lastName}`.trim()
                : 'Usuario'}
            </p>
            <p className="text-xs text-gray-500">
              {user?.email || 'usuario@ejemplo.com'}
            </p>
          </div>
          <div className="h-8 w-8 bg-proyecto-semilla-primary text-white rounded-full flex items-center justify-center text-sm font-medium">
            {userInitials}
          </div>
          <Button variant="ghost" size="icon" onClick={handleLogout}>
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
