import React, { useState, useEffect } from 'react';
import { MarketplaceGrid } from '@/components/marketplace/MarketplaceGrid';
import { PluginDetails } from '@/components/marketplace/PluginDetails';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  TrendingUp, Star, Download, Users,
  ArrowLeft, Grid, Sparkles
} from 'lucide-react';

// Mock data - in production this would come from the API
const mockPlugins = [
  {
    id: '1',
    name: 'Advanced Analytics Dashboard',
    description: 'Potente dashboard de analytics con visualizaciones avanzadas y reportes automáticos',
    version: '2.1.0',
    author: 'AnalyticsPro',
    rating: 4.8,
    reviewCount: 156,
    downloads: 12543,
    category: 'Analytics',
    tags: ['dashboard', 'reports', 'visualization', 'enterprise'],
    updatedAt: '2025-09-01T10:00:00Z',
    featured: true,
    verified: true,
    longDescription: 'Este plugin proporciona un sistema completo de analytics con dashboards interactivos, reportes automáticos y visualizaciones avanzadas. Incluye integración con múltiples fuentes de datos y exportación a diversos formatos.',
    screenshots: [
      'https://via.placeholder.com/800x600/4F46E5/FFFFFF?text=Dashboard+Preview',
      'https://via.placeholder.com/800x600/059669/FFFFFF?text=Reports+View'
    ],
    features: [
      'Dashboards interactivos en tiempo real',
      'Reportes automáticos programables',
      'Múltiples fuentes de datos',
      'Exportación a PDF, Excel y CSV',
      'Filtros avanzados y segmentación',
      'Alertas inteligentes'
    ],
    requirements: [
      'Proyecto Semilla v0.4.0+',
      'PostgreSQL para almacenamiento de métricas',
      'Redis para caching (opcional)'
    ],
    compatibility: ['v0.4.0', 'v0.4.1', 'v0.5.0'],
    documentationUrl: 'https://docs.proyecto-semilla.dev/plugins/analytics-dashboard',
    supportEmail: 'support@analyticspro.dev',
    license: 'MIT'
  },
  {
    id: '2',
    name: 'Real-time Collaboration Suite',
    description: 'Suite completa para colaboración en tiempo real con edición simultánea y chat integrado',
    version: '1.8.0',
    author: 'CollabTeam',
    rating: 4.6,
    reviewCount: 89,
    downloads: 8765,
    category: 'Collaboration',
    tags: ['real-time', 'collaboration', 'chat', 'editing'],
    updatedAt: '2025-08-28T14:30:00Z',
    featured: false,
    verified: true,
    longDescription: 'Transforma tu aplicación en una plataforma de colaboración completa. Incluye edición simultánea de documentos, chat en tiempo real, indicadores de presencia y sistema de notificaciones.',
    features: [
      'Edición simultánea de documentos',
      'Chat integrado con canales',
      'Indicadores de presencia en tiempo real',
      'Sistema de notificaciones push',
      'Historial de versiones',
      'Comentarios en documentos'
    ]
  },
  {
    id: '3',
    name: 'Security Audit Pro',
    description: 'Herramientas avanzadas de auditoría de seguridad con reportes detallados y compliance',
    version: '3.2.0',
    author: 'SecureDev',
    rating: 4.9,
    reviewCount: 234,
    downloads: 15234,
    category: 'Security',
    tags: ['security', 'audit', 'compliance', 'reports'],
    updatedAt: '2025-09-03T09:15:00Z',
    featured: true,
    verified: true
  },
  {
    id: '4',
    name: 'Workflow Automation Engine',
    description: 'Motor de automatización de flujos de trabajo con diseñador visual y triggers avanzados',
    version: '2.5.0',
    author: 'AutoFlow',
    rating: 4.4,
    reviewCount: 67,
    downloads: 5432,
    category: 'Workflow',
    tags: ['automation', 'workflow', 'triggers', 'visual-designer'],
    updatedAt: '2025-08-25T16:45:00Z',
    featured: false,
    verified: true
  },
  {
    id: '5',
    name: 'Multi-tenant Theme System',
    description: 'Sistema completo de temas personalizables por tenant con editor visual',
    version: '1.9.0',
    author: 'ThemeMaster',
    rating: 4.7,
    reviewCount: 123,
    downloads: 9876,
    category: 'UI/UX',
    tags: ['themes', 'customization', 'multi-tenant', 'visual-editor'],
    updatedAt: '2025-09-02T11:20:00Z',
    featured: false,
    verified: true
  }
];

const mockCategories = [
  'Analytics', 'Collaboration', 'Security', 'Workflow', 'UI/UX',
  'Integration', 'Business Logic', 'Communication'
];

const mockReviews = [
  {
    id: '1',
    userId: 'user1',
    userName: 'María González',
    rating: 5,
    title: 'Excelente plugin de analytics',
    comment: 'Este plugin ha transformado completamente cómo vemos nuestros datos. Las visualizaciones son increíbles y los reportes automáticos nos ahorran horas de trabajo.',
    pros: ['Fácil de configurar', 'Reportes automáticos', 'Excelente soporte'],
    cons: [],
    createdAt: '2025-08-30T10:00:00Z'
  },
  {
    id: '2',
    userId: 'user2',
    userName: 'Carlos Rodríguez',
    rating: 4,
    title: 'Muy buen plugin, pero podría mejorar',
    comment: 'Funciona muy bien para lo básico, pero echo de menos algunas funcionalidades avanzadas como integración con APIs externas.',
    pros: ['Interfaz intuitiva', 'Buen rendimiento'],
    cons: ['Falta integración con APIs externas'],
    createdAt: '2025-08-28T15:30:00Z'
  }
];

const Marketplace: React.FC = () => {
  const [plugins, setPlugins] = useState(mockPlugins);
  const [categories] = useState(mockCategories);
  const [selectedPlugin, setSelectedPlugin] = useState<any>(null);
  const [installedPlugins, setInstalledPlugins] = useState<string[]>(['2']); // Mock installed
  const [installingPlugins, setInstallingPlugins] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('browse');

  // Simulate loading plugins from API
  useEffect(() => {
    // In production, this would fetch from the API
    setPlugins(mockPlugins);
  }, []);

  const handleInstallPlugin = async (pluginId: string) => {
    setInstallingPlugins(prev => [...prev, pluginId]);

    // Simulate installation process
    setTimeout(() => {
      setInstalledPlugins(prev => [...prev, pluginId]);
      setInstallingPlugins(prev => prev.filter(id => id !== pluginId));
    }, 3000);
  };

  const handleViewPluginDetails = (pluginId: string) => {
    const plugin = plugins.find(p => p.id === pluginId);
    if (plugin) {
      setSelectedPlugin(plugin);
      setActiveTab('details');
    }
  };

  const handleBackToBrowse = () => {
    setSelectedPlugin(null);
    setActiveTab('browse');
  };

  const getStats = () => {
    const totalPlugins = plugins.length;
    const totalDownloads = plugins.reduce((sum, p) => sum + p.downloads, 0);
    const avgRating = plugins.reduce((sum, p) => sum + p.rating, 0) / plugins.length;
    const featuredPlugins = plugins.filter(p => p.featured).length;

    return { totalPlugins, totalDownloads, avgRating, featuredPlugins };
  };

  const stats = getStats();

  if (activeTab === 'details' && selectedPlugin) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="py-4">
              <Button
                variant="ghost"
                onClick={handleBackToBrowse}
                className="mb-4"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Volver al Marketplace
              </Button>
            </div>
          </div>
        </div>

        <PluginDetails
          plugin={selectedPlugin}
          reviews={mockReviews}
          onInstall={handleInstallPlugin}
          onClose={handleBackToBrowse}
          isInstalled={installedPlugins.includes(selectedPlugin.id)}
          isInstalling={installingPlugins.includes(selectedPlugin.id)}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  🛒 Marketplace de Plugins
                </h1>
                <p className="mt-2 text-gray-600">
                  Descubre y instala plugins para extender las funcionalidades de Proyecto Semilla
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-yellow-500" />
                <span className="text-sm text-gray-600">
                  {stats.featuredPlugins} plugins destacados
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="browse">Explorar</TabsTrigger>
            <TabsTrigger value="installed">Instalados ({installedPlugins.length})</TabsTrigger>
            <TabsTrigger value="trending">Tendencias</TabsTrigger>
          </TabsList>

          <TabsContent value="browse" className="mt-8">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Grid className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Total Plugins</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalPlugins}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Download className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Descargas Totales</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalDownloads.toLocaleString()}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      <Star className="w-6 h-6 text-yellow-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Calificación Promedio</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.avgRating.toFixed(1)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <Users className="w-6 h-6 text-purple-600" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600">Desarrolladores</p>
                      <p className="text-2xl font-bold text-gray-900">{new Set(plugins.map(p => p.author)).size}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Marketplace Grid */}
            <MarketplaceGrid
              plugins={plugins}
              onInstallPlugin={handleInstallPlugin}
              onViewPluginDetails={handleViewPluginDetails}
              installedPlugins={installedPlugins}
              installingPlugins={installingPlugins}
              categories={categories}
            />
          </TabsContent>

          <TabsContent value="installed" className="mt-8">
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Grid className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Plugins Instalados
              </h3>
              <p className="text-gray-600">
                Aquí aparecerán los plugins que hayas instalado.
              </p>
              <div className="mt-6">
                <Badge variant="secondary" className="mr-2">
                  {installedPlugins.length} instalado{installedPlugins.length !== 1 ? 's' : ''}
                </Badge>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="trending" className="mt-8">
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <TrendingUp className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Plugins en Tendencia
              </h3>
              <p className="text-gray-600">
                Los plugins más populares y descargados recientemente.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Marketplace;