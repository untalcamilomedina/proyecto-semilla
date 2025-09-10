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
  FileText,
  Eye,
  Calendar,
  User,
  Loader2
} from 'lucide-react';
import {
  useArticles,
  useDeleteArticle
} from '@/hooks/use-api';
import { ArticleQueryParams } from '@/types/api';

export default function ArticlesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'draft' | 'published' | 'review' | undefined>('published');

  // Build query params
  const queryParams: ArticleQueryParams = {
    status_filter: statusFilter,
    limit: 50
  };

  // Fetch data using React Query hooks
  const { data: articlesData, isLoading: articlesLoading } = useArticles(queryParams);
  const deleteArticleMutation = useDeleteArticle();

  const filteredArticles = articlesData?.filter((article: any) =>
    article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    article.excerpt.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const handleDeleteArticle = async (articleId: string) => {
    if (!confirm('¿Estás seguro de que quieres eliminar este artículo?')) return;

    try {
      await deleteArticleMutation.mutateAsync(articleId);
    } catch (error) {
      console.error('Error deleting article:', error);
    }
  };

  if (articlesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <div className="text-lg">Cargando artículos...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Artículos</h1>
          <p className="text-gray-600 mt-2">
            Administra contenido, categorías y publicaciones
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Nuevo Artículo
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Buscar y Filtrar Artículos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                type="text"
                placeholder="Buscar por título o extracto..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex space-x-2">
              {(['published', 'draft', 'review'] as const).map((status) => (
                <Button
                  key={status}
                  variant={statusFilter === status ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter(status)}
                >
                  {status === 'published' ? 'Publicado' :
                   status === 'draft' ? 'Borrador' : 'Revisión'}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Articles List */}
      <div className="space-y-4">
        {filteredArticles.map((article) => (
          <Card key={article.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {article.title}
                    </h3>
                    <Badge variant={
                      article.status === 'published' ? 'default' :
                      article.status === 'draft' ? 'secondary' : 'outline'
                    }>
                      {article.status === 'published' ? 'Publicado' :
                       article.status === 'draft' ? 'Borrador' : 'En Revisión'}
                    </Badge>
                  </div>

                  <p className="text-gray-600 mb-3 line-clamp-2">
                    {article.excerpt}
                  </p>

                  <div className="flex items-center space-x-6 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <User className="h-4 w-4" />
                      <span>{article.author_name || 'Autor desconocido'}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>{new Date(article.created_at).toLocaleDateString('es-ES')}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Eye className="h-4 w-4" />
                      <span>{article.view_count} vistas</span>
                    </div>
                    {article.category_name && (
                      <Badge variant="outline" className="text-xs">
                        {article.category_name}
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <Button variant="ghost" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteArticle(article.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredArticles.length === 0 && (
        <Card>
          <CardContent className="text-center py-8 text-gray-500">
            No se encontraron artículos
          </CardContent>
        </Card>
      )}
    </div>
  );
}