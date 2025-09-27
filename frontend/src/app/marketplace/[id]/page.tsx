'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { apiClient } from '@/lib/api-client';
import {
  Star,
  Download,
  ExternalLink,
  User,
  Calendar,
  Package,
  MessageSquare,
  ThumbsUp,
  ChevronLeft,
  ChevronRight,
  StarIcon
} from 'lucide-react';

interface ModuleDetails {
  id: string;
  module: {
    name: string;
    display_name: string;
    description: string;
    latest_version: string;
    author: string;
    homepage: string;
    repository?: string;
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
  reviews?: {
    items: Review[];
    pagination: {
      page: number;
      per_page: number;
      total_count: number;
      total_pages: number;
    };
  };
}

interface Review {
  id: string;
  user: {
    id: string;
    name: string;
    avatar?: string;
  };
  rating: number;
  title: string;
  content: string;
  pros: string[];
  cons: string[];
  helpful_votes: number;
  total_votes: number;
  is_verified_purchase: boolean;
  created_at: string;
}

export default function ModuleDetailsPage() {
  const params = useParams();
  const moduleId = params?.id as string;

  const [module, setModule] = useState<ModuleDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [installing, setInstalling] = useState(false);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    title: '',
    content: '',
    pros: [''],
    cons: ['']
  });
  const [submittingReview, setSubmittingReview] = useState(false);

  const loadModuleDetails = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/v1/marketplace/modules/${moduleId}`) as ModuleDetails;
      setModule(response);
    } catch (error) {
      console.error('Error loading module details:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (moduleId) {
      loadModuleDetails();
    }
  }, [moduleId]);

  const handleInstall = async () => {
    try {
      setInstalling(true);
      // Track download
      const response = await fetch(`/api/v1/marketplace/modules/${moduleId}/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to track download');
      }

      // Here you would typically redirect to installation or show installation modal
      alert('Módulo descargado exitosamente. La instalación comenzará pronto.');
    } catch (error) {
      console.error('Error installing module:', error);
      alert('Error al instalar el módulo. Por favor, inténtalo de nuevo.');
    } finally {
      setInstalling(false);
    }
  };

  const handleSubmitReview = async () => {
    try {
      setSubmittingReview(true);

      const reviewData = {
        rating: reviewForm.rating,
        title: reviewForm.title,
        content: reviewForm.content,
        pros: reviewForm.pros.filter(p => p.trim()),
        cons: reviewForm.cons.filter(c => c.trim())
      };

      const response = await fetch(`/api/v1/marketplace/modules/${moduleId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(reviewData),
      });

      if (!response.ok) {
        throw new Error('Failed to submit review');
      }

      // Reload module details to show new review
      await loadModuleDetails();

      // Reset form
      setReviewForm({
        rating: 5,
        title: '',
        content: '',
        pros: [''],
        cons: ['']
      });

      alert('Reseña enviada exitosamente.');
    } catch (error) {
      console.error('Error submitting review:', error);
      alert('Error al enviar la reseña. Por favor, inténtalo de nuevo.');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleAddRating = async (rating: number) => {
    try {
      const response = await fetch(`/api/v1/marketplace/modules/${moduleId}/ratings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ rating }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit rating');
      }
      await loadModuleDetails();
      alert('Calificación enviada exitosamente.');
    } catch (error) {
      console.error('Error submitting rating:', error);
      alert('Error al enviar la calificación.');
    }
  };

  const renderStars = (rating: number, interactive: boolean = false, onRate?: (rating: number) => void) => {
    return (
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            className={`h-5 w-5 ${interactive ? 'cursor-pointer hover:scale-110' : ''} ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
            onClick={interactive && onRate ? () => onRate(star) : undefined}
            disabled={!interactive}
          >
            <Star className="h-5 w-5" />
          </button>
        ))}
        <span className="text-sm text-gray-600 ml-2">
          {rating.toFixed(1)}
        </span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Cargando detalles del módulo...</div>
      </div>
    );
  }

  if (!module) {
    return (
      <div className="text-center py-12">
        <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Módulo no encontrado
        </h3>
        <p className="text-gray-600">
          El módulo que buscas no existe o no está disponible.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <Button variant="ghost" size="sm">
              <ChevronLeft className="h-4 w-4 mr-1" />
              Volver al marketplace
            </Button>
          </div>

          <div className="flex items-start space-x-4">
            <Package className="h-12 w-12 text-gray-400 flex-shrink-0" />

            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h1 className="text-3xl font-bold">{module.module.display_name}</h1>
                {module.flags.is_featured && (
                  <Badge variant="secondary">Destacado</Badge>
                )}
                {module.flags.is_verified && (
                  <Badge variant="outline">Verificado</Badge>
                )}
                {module.flags.is_deprecated && (
                  <Badge variant="destructive">Obsoleto</Badge>
                )}
              </div>

              <p className="text-lg text-gray-600 mb-4">{module.module.description}</p>

              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <div className="flex items-center space-x-1">
                  <User className="h-4 w-4" />
                  <span>{module.publisher.name}</span>
                </div>

                <div className="flex items-center space-x-1">
                  <Package className="h-4 w-4" />
                  <span>{module.category.display_name}</span>
                </div>

                <div className="flex items-center space-x-1">
                  <Calendar className="h-4 w-4" />
                  <span>v{module.module.latest_version}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col space-y-3">
          <div className="text-center">
            {renderStars(module.stats.rating)}
            <div className="text-sm text-gray-600 mt-1">
              {module.stats.total_ratings} calificaciones
            </div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold">{module.stats.downloads.toLocaleString()}</div>
            <div className="text-sm text-gray-600">descargas</div>
          </div>

          <div className="flex space-x-2">
            <Button
              onClick={handleInstall}
              disabled={installing}
              className="flex-1"
            >
              <Download className="h-4 w-4 mr-2" />
              {installing ? 'Instalando...' : 'Instalar'}
            </Button>

            {module.demo_url && (
              <Button variant="outline" asChild>
                <a href={module.demo_url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Tags and Links */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex flex-wrap gap-2">
              {module.tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>

            <div className="flex space-x-2 ml-auto">
              {module.documentation_url && (
                <Button variant="outline" size="sm" asChild>
                  <a href={module.documentation_url} target="_blank" rel="noopener noreferrer">
                    Documentación
                  </a>
                </Button>
              )}

              {module.module.repository && (
                <Button variant="outline" size="sm" asChild>
                  <a href={module.module.repository} target="_blank" rel="noopener noreferrer">
                    Código fuente
                  </a>
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="reviews">Reseñas ({module.stats.total_reviews})</TabsTrigger>
          <TabsTrigger value="screenshots">Capturas</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Descripción</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">
                    {module.module.description}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Información del módulo</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Versión:</span> {module.module.latest_version}
                    </div>
                    <div>
                      <span className="font-medium">Autor:</span> {module.module.author}
                    </div>
                    <div>
                      <span className="font-medium">Licencia:</span> {module.pricing.license_type || 'No especificada'}
                    </div>
                    <div>
                      <span className="font-medium">Publicado:</span> {new Date(module.published_at || module.last_updated).toLocaleDateString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Estadísticas</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    {renderStars(module.stats.rating)}
                    <div className="text-sm text-gray-600 mt-1">
                      Basado en {module.stats.total_ratings} calificaciones
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="text-2xl font-bold">{module.stats.downloads.toLocaleString()}</div>
                    <div className="text-sm text-gray-600">descargas totales</div>
                  </div>

                  <div className="text-center">
                    <div className="text-lg font-semibold">
                      {module.pricing.model === 'free' ? (
                        <span className="text-green-600">Gratuito</span>
                      ) : (
                        <span>${module.pricing.price} {module.pricing.currency}</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 capitalize">{module.pricing.model}</div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Calificar módulo</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center space-y-3">
                    <div>¿Qué te parece este módulo?</div>
                    {renderStars(0, true, handleAddRating)}
                    <div className="text-sm text-gray-600">
                      Tu calificación será anónima
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="reviews" className="space-y-4">
          {/* Write Review */}
          <Card>
            <CardHeader>
              <CardTitle>Escribir reseña</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="rating">Calificación</Label>
                <div className="mt-2">
                  {renderStars(reviewForm.rating, true, (rating) =>
                    setReviewForm(prev => ({ ...prev, rating }))
                  )}
                </div>
              </div>

              <div>
                <Label htmlFor="title">Título de la reseña</Label>
                <Input
                  id="title"
                  value={reviewForm.title}
                  onChange={(e) => setReviewForm(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Resumen de tu experiencia..."
                />
              </div>

              <div>
                <Label htmlFor="content">Reseña detallada</Label>
                <Textarea
                  id="content"
                  value={reviewForm.content}
                  onChange={(e) => setReviewForm(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Comparte tu experiencia con este módulo..."
                  rows={4}
                />
              </div>

              <Button
                onClick={handleSubmitReview}
                disabled={submittingReview || !reviewForm.title.trim() || !reviewForm.content.trim()}
              >
                {submittingReview ? 'Enviando...' : 'Enviar reseña'}
              </Button>
            </CardContent>
          </Card>

          {/* Reviews List */}
          {module.reviews && module.reviews.items.map((review) => (
            <Card key={review.id}>
              <CardContent className="pt-6">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <User className="h-5 w-5 text-gray-500" />
                    </div>
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium">{review.user.name}</span>
                      {review.is_verified_purchase && (
                        <Badge variant="outline" className="text-xs">
                          Compra verificada
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 mb-3">
                      {renderStars(review.rating)}
                      <span className="text-sm text-gray-600">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <h4 className="font-medium mb-2">{review.title}</h4>
                    <p className="text-gray-700 mb-3">{review.content}</p>

                    {review.pros.length > 0 && (
                      <div className="mb-2">
                        <span className="font-medium text-green-600">Pros:</span>
                        <ul className="list-disc list-inside ml-4 text-sm text-gray-600">
                          {review.pros.map((pro, index) => (
                            <li key={index}>{pro}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {review.cons.length > 0 && (
                      <div className="mb-3">
                        <span className="font-medium text-red-600">Cons:</span>
                        <ul className="list-disc list-inside ml-4 text-sm text-gray-600">
                          {review.cons.map((con, index) => (
                            <li key={index}>{con}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <button className="flex items-center space-x-1 hover:text-gray-900">
                        <ThumbsUp className="h-4 w-4" />
                        <span>Útil ({review.helpful_votes})</span>
                      </button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="screenshots" className="space-y-4">
          {module.screenshots.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {module.screenshots.map((screenshot, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <img
                      src={screenshot}
                      alt={`Captura ${index + 1}`}
                      className="w-full h-auto rounded-lg"
                    />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No hay capturas disponibles para este módulo.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}