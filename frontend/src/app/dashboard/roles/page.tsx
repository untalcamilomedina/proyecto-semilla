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
  Shield,
  Users,
  Settings,
  Check
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Role } from '@/types/api';
import { usePermissionCheck } from '@/hooks/usePermissions';
import { useRoles, useDeleteRole } from '@/hooks/use-api';

export default function RolesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Permission checks
  const { canWriteRoles, canDeleteRoles } = usePermissionCheck();

  // Fetch roles using React Query hook
  const { data: roles, isLoading } = useRoles();
  const deleteRoleMutation = useDeleteRole();

  const filteredRoles = (roles || []).filter(role =>
    role.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    role.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeleteRole = async (roleId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este rol?')) return;

    try {
      await deleteRoleMutation.mutateAsync(roleId);
    } catch (error) {
      console.error('Error deleting role:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Cargando roles...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sistema de Roles y Permisos</h1>
          <p className="text-gray-600 mt-2">
            Gestiona roles, permisos y control de acceso granular
          </p>
        </div>
        {canWriteRoles() && (
          <Button onClick={() => setShowCreateForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Nuevo Rol
          </Button>
        )}
      </div>

      {/* Search */}
      <Card>
        <CardHeader>
          <CardTitle>Buscar Roles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              type="text"
              placeholder="Buscar por nombre o descripción..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Roles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredRoles.map((role) => (
          <Card key={role.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 bg-proyecto-semilla-primary text-white rounded-lg flex items-center justify-center">
                    <Shield className="h-5 w-5" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{role.name}</CardTitle>
                    {role.hierarchy_level >= 500 && (
                      <Badge variant="secondary" className="text-xs">
                        Sistema
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {role.description && (
                  <p className="text-sm text-gray-600">{role.description}</p>
                )}

                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    Permisos ({role.permissions.length})
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {role.permissions.slice(0, 3).map((permission: string, index: number) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {permission}
                      </Badge>
                    ))}
                    {role.permissions.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{role.permissions.length - 3} más
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Users className="h-4 w-4" />
                    <span>-- usuarios</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Button variant="ghost" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    {role.hierarchy_level < 500 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteRole(role.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredRoles.length === 0 && (
        <Card>
          <CardContent className="text-center py-8 text-gray-500">
            No se encontraron roles
          </CardContent>
        </Card>
      )}

      {/* Common Permissions Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Permisos Comunes del Sistema</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">Usuarios</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>users:read</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>users:create</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>users:update</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>users:delete</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">Artículos</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>articles:read</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>articles:create</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>articles:publish</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">Sistema</h4>
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>system:admin</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>tenants:manage</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Check className="h-3 w-3 text-green-500" />
                  <span>roles:manage</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}