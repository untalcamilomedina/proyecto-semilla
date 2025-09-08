'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Users,
  Building2,
  FileText,
  TrendingUp,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  Loader2
} from 'lucide-react';
import {
  useUsers,
  useTenants,
  useRoles,
  useArticleStats,
  useCategoryStats
} from '@/hooks/use-api';

export default function DashboardPage() {
  // Fetch data using React Query hooks
  const { data: users, isLoading: usersLoading } = useUsers();
  const { data: tenants, isLoading: tenantsLoading } = useTenants();
  const { data: roles, isLoading: rolesLoading } = useRoles();
  const { data: articleStats, isLoading: articleStatsLoading } = useArticleStats();
  const { data: categoryStats, isLoading: categoryStatsLoading } = useCategoryStats();

  // Calculate derived stats
  const totalUsers = users?.length || 0;
  const activeUsers = users?.filter(user => user.is_active).length || 0;
  const totalTenants = tenants?.length || 0;
  const activeTenants = tenants?.filter(tenant => tenant.is_active).length || 0;
  const totalRoles = roles?.length || 0;

  const isLoading = usersLoading || tenantsLoading || rolesLoading || articleStatsLoading || categoryStatsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <div className="text-lg">Cargando estadísticas...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Administrativo</h1>
        <p className="text-gray-600 mt-2">
          Bienvenido al panel de administración de Proyecto Semilla
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Usuarios</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              {activeUsers} activos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tenants</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalTenants}</div>
            <p className="text-xs text-muted-foreground">
              {activeTenants} activos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Artículos</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{articleStats?.total_articles || 0}</div>
            <p className="text-xs text-muted-foreground">
              {articleStats?.published_articles || 0} publicados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Roles</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalRoles}</div>
            <p className="text-xs text-muted-foreground">
              Roles del sistema
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Actividad Reciente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm font-medium">Nuevo usuario registrado</p>
                  <p className="text-xs text-gray-500">Hace 2 minutos</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-sm font-medium">Artículo publicado</p>
                  <p className="text-xs text-gray-500">Hace 15 minutos</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Building2 className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="text-sm font-medium">Nuevo tenant creado</p>
                  <p className="text-xs text-gray-500">Hace 1 hora</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alertas del Sistema</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <AlertCircle className="h-5 w-5 text-yellow-500" />
                <div>
                  <p className="text-sm font-medium">Usuario inactivo por 30 días</p>
                  <p className="text-xs text-gray-500">5 usuarios afectados</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Clock className="h-5 w-5 text-orange-500" />
                <div>
                  <p className="text-sm font-medium">Artículos pendientes de revisión</p>
                  <p className="text-xs text-gray-500">12 artículos en cola</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Acciones Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button>
              <Users className="mr-2 h-4 w-4" />
              Crear Usuario
            </Button>
            <Button variant="outline">
              <Building2 className="mr-2 h-4 w-4" />
              Nuevo Tenant
            </Button>
            <Button variant="outline">
              <FileText className="mr-2 h-4 w-4" />
              Publicar Artículo
            </Button>
            <Button variant="outline">
              <TrendingUp className="mr-2 h-4 w-4" />
              Ver Reportes
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}