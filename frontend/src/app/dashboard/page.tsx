'use client';

import { useApi } from '@/hooks/use-api';
import { StatCard } from '@/components/dashboard/stat-card';
import { UsersChart } from '@/components/dashboard/users-chart';
import { RecentUsers } from '@/components/dashboard/recent-users';
import { Loader2, Users, Building2, Shield } from 'lucide-react';
import { User } from '@/types/api';

// Definir los tipos para los datos del dashboard
interface DashboardMetrics {
  user_count: number;
  tenant_count: number;
  role_count: number;
}

interface UsersOverTimeData {
  date: string;
  count: number;
}

export default function DashboardPage() {

  const { data: metrics, isLoading: metricsLoading } = useApi<DashboardMetrics>('dashboard/metrics');
  const { data: usersOverTime, isLoading: usersOverTimeLoading } = useApi<UsersOverTimeData[]>('dashboard/users-over-time');
  const { data: recentUsers, isLoading: recentUsersLoading } = useApi<User[]>('dashboard/recent-users');

  const isLoading = metricsLoading || usersOverTimeLoading || recentUsersLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Users" value={metrics?.user_count || 0} icon={Users} />
        <StatCard title="Total Tenants" value={metrics?.tenant_count || 0} icon={Building2} />
        <StatCard title="Total Roles" value={metrics?.role_count || 0} icon={Shield} />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4">
          {usersOverTime && <UsersChart data={usersOverTime} />}
        </div>
        <div className="col-span-3">
          {recentUsers && <RecentUsers users={recentUsers} />}
        </div>
      </div>
    </div>
  );
}
