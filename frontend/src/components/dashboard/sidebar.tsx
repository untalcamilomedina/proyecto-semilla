'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { usePermissionCheck } from '@/hooks/usePermissions';
import { PERMISSIONS } from '@/types/api';
import {
  LayoutDashboard,
  Users,
  Building2,
  FileText,
  Shield,
  Settings,
  Bell,
  BarChart3
} from 'lucide-react';

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    permissions: [] // Dashboard is always accessible
  },
  {
    name: 'Usuarios',
    href: '/dashboard/users',
    icon: Users,
    permissions: [PERMISSIONS.USERS_READ]
  },
  {
    name: 'Tenants',
    href: '/dashboard/tenants',
    icon: Building2,
    permissions: [PERMISSIONS.TENANTS_READ]
  },
  {
    name: 'Artículos',
    href: '/dashboard/articles',
    icon: FileText,
    permissions: [PERMISSIONS.ARTICLES_READ]
  },
  {
    name: 'Roles',
    href: '/dashboard/roles',
    icon: Shield,
    permissions: [PERMISSIONS.ROLES_READ]
  },
  {
    name: 'Estadísticas',
    href: '/dashboard/stats',
    icon: BarChart3,
    permissions: [PERMISSIONS.ARTICLES_READ] // Basic read permission for stats
  },
  {
    name: 'Notificaciones',
    href: '/dashboard/notifications',
    icon: Bell,
    permissions: [] // Notifications might be user-specific
  },
  {
    name: 'Configuración',
    href: '/dashboard/settings',
    icon: Settings,
    permissions: [PERMISSIONS.SYSTEM_CONFIG]
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { canAccess } = usePermissionCheck();

  // Filter navigation items based on permissions
  const accessibleNavigation = navigation.filter(item => {
    // If no permissions required, always show
    if (!item.permissions || item.permissions.length === 0) {
      return true;
    }
    // Check if user has any of the required permissions
    return canAccess(item.permissions);
  });

  return (
    <div className="flex h-full w-64 flex-col bg-white border-r border-gray-200">
      <div className="flex h-16 items-center px-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-proyecto-semilla-primary">
          Proyecto Semilla 🌱
        </h1>
      </div>
      <nav className="flex-1 space-y-1 px-4 py-4">
        {accessibleNavigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-proyecto-semilla-primary text-white'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              <item.icon
                className={cn(
                  'mr-3 h-5 w-5 flex-shrink-0',
                  isActive ? 'text-white' : 'text-gray-400 group-hover:text-gray-500'
                )}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}