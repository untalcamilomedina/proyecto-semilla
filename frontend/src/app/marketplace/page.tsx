'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/api-client';
import {
  Search,
  Star,
  Download,
  Filter,
  Grid,
  List,
  Package,
  User,
  Calendar,
  ExternalLink,
  StarIcon,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface MarketplaceCategory {
  id: string;
  name: string;
  display_name: string;
  description: string;
  icon: string;
  color: string;
  sort_order: number;
}

interface MarketplaceModule {
  id: string;
  module: {
    name: string;
    display_name: string;
    description: string;
    latest_version: string;
    author: string;
    homepage: string;
    repository: string;
    is_official: boolean;
  };
  category: {
    id: string;
    name: string;
    display_name: string;
    icon: string;
  };
  tags: string[];
  screenshots: string[];
  demo_url?: string;
  documentation_url?: string;
  support_email?: string;
  pricing: {
    model: string;
    price?: number;
    currency: string;
    license_type?: string;
  };
  publisher: {
    name: string;
    email: string;
  };
  stats: {
    downloads: number;
    rating: number;
    total_ratings: number;
    total_reviews: number;
  };
  flags: {
    is_featured: boolean;
    is_verified: boolean;
    is_deprecated: boolean;
  };
  published_at?: string;
  last_updated: string;
}

interface SearchResult {
  modules: MarketplaceModule[];
  pagination: {
    page: number;
    per_page: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  filters_applied: {
    query?: string;
    category?: string;
    tags?: string[];
    pricing_model?: string;
    min_rating?: number;
    publisher?: string;
    is_featured?: boolean;
    is_verified?: boolean;
  };
}

export default function MarketplacePage() {
  const [categories, setCategories] = useState<MarketplaceCategory[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);

  // Search filters
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedPricing, setSelectedPricing] = useState<string>('');
  const [minRating, setMinRating] = useState<string>('');
  const [sortBy, setSortBy] = useState('downloads');
  const [sortOrder, setSortOrder] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const loadCategories = async () => {
    try {
      const response = await apiClient.get('/api/v1/marketplace/categories') as MarketplaceCategory[];
      setCategories(response);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const performSearch = async (page: number = 1) => {
    try {
      setSearching(true);

      const params: any = {
        page,
        per_page: 20,
        sort_by: sortBy,
        sort_order: sortOrder
      };

      if (query.trim()) params.q = query.trim();
      if (selectedCategory) params.category = selectedCategory;
      if (selectedPricing) params.pricing_model = selectedPricing;
      if (minRating) params.min_rating = parseFloat(minRating);

      const response = await apiClient.get('/api/v1/marketplace/search', { params }) as SearchResult;
      setSearchResults(response);
      setCurrentPage(page);
    } catch (error) {
      console.error('Error searching modules:', error);
    } finally {
      setSearching(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
    performSearch();
  }, []);

  const handleSearch = () => {
    performSearch(1);
  };

  const handlePageChange = (page: number) => {
    performSearch(page);
  };

  const handleCategoryClick = (categoryName: string) => {
    setSelectedCategory(categoryName);
    setTimeout(() => performSearch(1), 0);
  };

  const clearFilters = () => {
    setQuery('');
    setSelectedCategory('');
    setSelectedPricing('');
    setMinRating('');
    setSortBy('downloads');
    setSortOrder('desc');
    setCurrentPage(1);
    performSearch(1);
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-4 w-4 ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="text-sm text-gray-600 ml-1">
          {rating.toFixed(1)}
        </span>
      </div>
    );
  };

  const ModuleCard = ({ module }: { module: MarketplaceModule }) => (
    <Card className="h-full hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg line-clamp-1">
              {module.module.display_name}
            </CardTitle>
            <CardDescription className="line-clamp-2 mt-1">
              {module.module.description}
            </CardDescription>
          </div>
          {module.flags.is_featured && (
            <Badge variant="secondary" className="ml-2">
              Destacado
            </Badge>
          )}
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <User className="h-4 w-4" />
          <span>{module.publisher.name}</span>
          {module.flags.is_verified && (
            <Badge variant="outline" className="text-xs">
              Verificado
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-3">
          {/* Category and Tags */}
          <div className="flex items-center space-x-2">
            <Badge variant="outline">
              {module.category.icon} {module.category.display_name}
            </Badge>
            {module.tags.slice(0, 2).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>

          {/* Stats */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <Download className="h-4 w-4 text-gray-500" />
                <span>{module.stats.downloads.toLocaleString()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Star className="h-4 w-4 text-gray-500" />
                <span>{module.stats.total_ratings}</span>
              </div>
            </div>
            {renderStars(module.stats.rating)}
          </div>

          {/* Pricing */}
          <div className="flex items-center justify-between">
            <div className="text-sm">
              {module.pricing.model === 'free' ? (
                <Badge variant="outline" className="text-green-600">
                  Gratuito
                </Badge>
              ) : module.pricing.model === 'paid' ? (
                <Badge variant="outline">
                  ${module.pricing.price}/{module.pricing.currency}
                </Badge>
              ) : (
                <Badge variant="outline">
                  {module.pricing.model}
                </Badge>
              )}
            </div>
            <Button size="sm" variant="outline">
              Ver detalles
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const ModuleListItem = ({ module }: { module: MarketplaceModule }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            <Package className="h-8 w-8 text-gray-400" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-medium text-gray-900 truncate">
                {module.module.display_name}
              </h3>
              {module.flags.is_featured && (
                <Badge variant="secondary">Destacado</Badge>
              )}
              {module.flags.is_verified && (
                <Badge variant="outline">Verificado</Badge>
              )}
            </div>

            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
              {module.module.description}
            </p>

            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
              <span>{module.publisher.name}</span>
              <span>•</span>
              <span>{module.category.display_name}</span>
              <span>•</span>
              <span>v{module.module.latest_version}</span>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <div className="text-center">
              {renderStars(module.stats.rating)}
              <div className="text-xs text-gray-500 mt-1">
                {module.stats.total_ratings} calificaciones
              </div>
            </div>

            <div className="text-center">
              <div className="flex items-center space-x-1">
                <Download className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium">
                  {module.stats.downloads.toLocaleString()}
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-1">descargas</div>
            </div>

            <div className="text-center">
              {module.pricing.model === 'free' ? (
                <Badge variant="outline" className="text-green-600">
                  Gratuito
                </Badge>
              ) : (
                <Badge variant="outline">
                  ${module.pricing.price}
                </Badge>
              )}
            </div>

            <Button size="sm">
              Instalar
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Cargando marketplace...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Marketplace de Módulos</h1>
          <p className="text-gray-600">Descubre y instala módulos para extender tu plataforma</p>
        </div>
        <Button>
          <Package className="h-4 w-4 mr-2" />
          Publicar Módulo
        </Button>
      </div>

      {/* Categories */}
      <Card>
        <CardHeader>
          <CardTitle>Categorías</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedCategory === '' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleCategoryClick('')}
            >
              Todas
            </Button>
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.name ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleCategoryClick(category.name)}
              >
                {category.icon} {category.display_name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Buscar módulos..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="pl-10"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>

            <div className="flex gap-2">
              <Select value={selectedPricing} onValueChange={setSelectedPricing}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Precio" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="free">Gratuito</SelectItem>
                  <SelectItem value="paid">Pago</SelectItem>
                  <SelectItem value="freemium">Freemium</SelectItem>
                </SelectContent>
              </Select>

              <Select value={minRating} onValueChange={setMinRating}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Rating mín." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos</SelectItem>
                  <SelectItem value="4">4+ estrellas</SelectItem>
                  <SelectItem value="3">3+ estrellas</SelectItem>
                  <SelectItem value="2">2+ estrellas</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Ordenar por" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="downloads">Descargas</SelectItem>
                  <SelectItem value="rating">Rating</SelectItem>
                  <SelectItem value="name">Nombre</SelectItem>
                  <SelectItem value="updated">Actualizado</SelectItem>
                </SelectContent>
              </Select>

              <Button onClick={handleSearch} disabled={searching}>
                {searching ? 'Buscando...' : 'Buscar'}
              </Button>

              <Button variant="outline" onClick={clearFilters}>
                Limpiar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Header */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {searchResults ? `${searchResults.pagination.total_count} módulos encontrados` : 'Cargando...'}
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            <Grid className="h-4 w-4" />
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Results */}
      {searchResults && (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {searchResults.modules.map((module) => (
                <ModuleCard key={module.id} module={module} />
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {searchResults.modules.map((module) => (
                <ModuleListItem key={module.id} module={module} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {searchResults.pagination.total_pages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-8">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={!searchResults.pagination.has_prev}
              >
                <ChevronLeft className="h-4 w-4" />
                Anterior
              </Button>

              <span className="text-sm text-gray-600">
                Página {currentPage} de {searchResults.pagination.total_pages}
              </span>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={!searchResults.pagination.has_next}
              >
                Siguiente
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}

      {/* Empty State */}
      {searchResults && searchResults.modules.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No se encontraron módulos
            </h3>
            <p className="text-gray-600 mb-4">
              Intenta ajustar tus filtros de búsqueda o explora otras categorías.
            </p>
            <Button onClick={clearFilters}>
              Limpiar filtros
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}