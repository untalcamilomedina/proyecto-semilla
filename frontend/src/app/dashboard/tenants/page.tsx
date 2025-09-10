'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Plus,
  Search,
  Edit,
  Trash2,
  Building2,
  Globe,
  Users,
  Settings,
  Loader2
} from 'lucide-react';
import {
  useTenants,
  useUpdateTenant,
  useDeleteTenant,
  useUsers
} from '@/hooks/use-api';
import { User } from '@/types/api';

export default function TenantsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Fetch data using React Query hooks
  const { data: tenants, isLoading: tenantsLoading } = useTenants();
  const { data: users } = useUsers();
  const updateTenantMutation = useUpdateTenant();
  const deleteTenantMutation = useDeleteTenant();

  // Calculate users per tenant
  const usersPerTenant = users?.reduce((acc, user) => {
    acc[user.tenant_id] = (acc[user.tenant_id] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  const filteredTenants = tenants?.filter(tenant =>
    tenant.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tenant.slug.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const handleToggleTenantStatus = async (tenantId: string, currentStatus: boolean) => {
    try {
      await updateTenantMutation.mutateAsync({
        id: tenantId,
        tenant: { is_active: !currentStatus }
      });
    } catch (error) {
      console.error('Error updating tenant status:', error);
    }
  };

  const handleDeleteTenant = async (tenantId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este tenant?')) return;

    try {
      await deleteTenantMutation.mutateAsync(tenantId);
    } catch (error) {
      console.error('Error deleting tenant:', error);
    }
  };

  if (tenantsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <div className="text-lg">Cargando tenants...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Tenants</h1>
          <p className="text-gray-600 mt-2">
            Administra organizaciones y configuraciones multi-tenant
          </p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Nuevo Tenant
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Buscar Tenants</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                type="text"
                placeholder="Buscar por nombre o slug..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">Filtrar</Button>
          </div>
        </CardContent>
      </Card>

      {/* Tenants Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTenants.map((tenant) => (
          <Card key={tenant.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 bg-proyecto-semilla-primary text-white rounded-lg flex items-center justify-center">
                    <Building2 className="h-5 w-5" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{tenant.name}</CardTitle>
                    <p className="text-sm text-gray-500">@{tenant.slug}</p>
                  </div>
                </div>
                <Badge variant={tenant.is_active ? 'default' : 'destructive'}>
                  {tenant.is_active ? 'Activo' : 'Inactivo'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {tenant.domain && (
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Globe className="h-4 w-4" />
                    <span>{tenant.domain}</span>
                  </div>
                )}

                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Users className="h-4 w-4" />
                  <span>Usuarios: {usersPerTenant[tenant.id] || 0}</span>
                </div>

                <div className="text-xs text-gray-500">
                  Creado: {new Date(tenant.created_at).toLocaleDateString('es-ES')}
                </div>

                <div className="flex items-center justify-between pt-2">
                  <Button variant="outline" size="sm">
                    <Settings className="mr-2 h-4 w-4" />
                    Configurar
                  </Button>
                  <div className="flex items-center space-x-1">
                    <Button variant="ghost" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleTenantStatus(tenant.id, tenant.is_active)}
                    >
                      {tenant.is_active ? 'Desactivar' : 'Activar'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteTenant(tenant.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredTenants.length === 0 && (
        <Card>
          <CardContent className="text-center py-8 text-gray-500">
            No se encontraron tenants
          </CardContent>
        </Card>
      )}
    </div>
  );
}