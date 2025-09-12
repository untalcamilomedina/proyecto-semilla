import React, { useState, useMemo } from 'react';
import { PluginCard } from './PluginCard';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Filter, Grid, List, SortAsc, SortDesc } from 'lucide-react';

interface MarketplaceGridProps {
  plugins: any[];
  onInstallPlugin?: (pluginId: string) => void;
  onViewPluginDetails?: (pluginId: string) => void;
  installedPlugins?: string[];
  installingPlugins?: string[];
  categories?: string[];
  loading?: boolean;
}

type SortOption = 'name' | 'rating' | 'downloads' | 'updated' | 'relevance';
type ViewMode = 'grid' | 'list';

export const MarketplaceGrid: React.FC<MarketplaceGridProps> = ({
  plugins,
  onInstallPlugin,
  onViewPluginDetails,
  installedPlugins = [],
  installingPlugins = [],
  categories = [],
  loading = false
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  // Filter and sort plugins
  const filteredAndSortedPlugins = useMemo(() => {
    const filtered = plugins.filter(plugin => {
      const matchesSearch = !searchQuery ||
        plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.tags.some((tag: string) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesCategory = selectedCategory === 'all' || plugin.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });

    // Sort plugins
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'rating':
          aValue = a.rating;
          bValue = b.rating;
          break;
        case 'downloads':
          aValue = a.downloads;
          bValue = b.downloads;
          break;
        case 'updated':
          aValue = new Date(a.updatedAt).getTime();
          bValue = new Date(b.updatedAt).getTime();
          break;
        case 'relevance':
        default:
          // Simple relevance score based on rating and downloads
          aValue = (a.rating * 0.7) + (Math.log(a.downloads + 1) * 0.3);
          bValue = (b.rating * 0.7) + (Math.log(b.downloads + 1) * 0.3);
          break;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [plugins, searchQuery, selectedCategory, sortBy, sortOrder]);

  const handleSortChange = (newSortBy: SortOption) => {
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('desc');
    }
  };

  const getSortIcon = (option: SortOption) => {
    if (sortBy !== option) return null;
    return sortOrder === 'asc' ?
      <SortAsc className="w-4 h-4 ml-1" /> :
      <SortDesc className="w-4 h-4 ml-1" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Cargando plugins...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg border shadow-sm">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Buscar plugins..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Category Filter */}
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-full lg:w-48">
              <Filter className="w-4 h-4 mr-2" />
              <SelectValue placeholder="Categoría" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todas las categorías</SelectItem>
              {categories.map(category => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* View Mode Toggle */}
          <div className="flex border rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              className="rounded-r-none"
            >
              <Grid className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className="rounded-l-none"
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Sort Options */}
        <div className="flex flex-wrap gap-2 mt-4">
          <span className="text-sm text-gray-600 mr-2">Ordenar por:</span>
          {[
            { key: 'relevance' as SortOption, label: 'Relevancia' },
            { key: 'rating' as SortOption, label: 'Calificación' },
            { key: 'downloads' as SortOption, label: 'Descargas' },
            { key: 'updated' as SortOption, label: 'Actualización' },
            { key: 'name' as SortOption, label: 'Nombre' }
          ].map(option => (
            <Button
              key={option.key}
              variant={sortBy === option.key ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleSortChange(option.key)}
              className="flex items-center"
            >
              {option.label}
              {getSortIcon(option.key)}
            </Button>
          ))}
        </div>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          {filteredAndSortedPlugins.length} plugin{filteredAndSortedPlugins.length !== 1 ? 's' : ''} encontrado{filteredAndSortedPlugins.length !== 1 ? 's' : ''}
          {searchQuery && (
            <span> para <strong>&quot;{searchQuery}&quot;</strong></span>
          )}
          {selectedCategory !== 'all' && (
            <span> en <Badge variant="secondary">{selectedCategory}</Badge></span>
          )}
        </div>
      </div>

      {/* Plugins Grid/List */}
      {filteredAndSortedPlugins.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No se encontraron plugins
          </h3>
          <p className="text-gray-600">
            Intenta ajustar tus filtros de búsqueda o explora otras categorías.
          </p>
        </div>
      ) : (
        <div className={
          viewMode === 'grid'
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            : "space-y-4"
        }>
          {filteredAndSortedPlugins.map(plugin => (
            <PluginCard
              key={plugin.id}
              plugin={plugin}
              onInstall={onInstallPlugin}
              onViewDetails={onViewPluginDetails}
              isInstalled={installedPlugins.includes(plugin.id)}
              isInstalling={installingPlugins.includes(plugin.id)}
            />
          ))}
        </div>
      )}

      {/* Load More (if needed) */}
      {filteredAndSortedPlugins.length > 0 && filteredAndSortedPlugins.length % 20 === 0 && (
        <div className="text-center py-6">
          <Button variant="outline">
            Cargar más plugins
          </Button>
        </div>
      )}
    </div>
  );
};