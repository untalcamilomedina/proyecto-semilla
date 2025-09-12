import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import {
  Star, Download, Heart, ExternalLink, Calendar, User,
  Shield, CheckCircle, AlertCircle,
  ThumbsUp, ThumbsDown, MessageSquare
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface PluginDetailsProps {
  plugin: {
    id: string;
    name: string;
    description: string;
    version: string;
    author: string;
    rating: number;
    reviewCount: number;
    downloads: number;
    category: string;
    tags: string[];
    updatedAt: string;
    featured?: boolean;
    verified?: boolean;
    longDescription?: string;
    screenshots?: string[];
    documentationUrl?: string;
    supportEmail?: string;
    license?: string;
    compatibility?: string[];
    features?: string[];
    requirements?: string[];
  };
  reviews?: any[];
  onInstall?: (pluginId: string) => void;
  onClose?: () => void;
  isInstalled?: boolean;
  isInstalling?: boolean;
}

export const PluginDetails: React.FC<PluginDetailsProps> = ({
  plugin,
  reviews = [],
  onInstall,
  isInstalled = false,
  isInstalling = false
}) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isLiked, setIsLiked] = useState(false);

  const handleInstall = () => {
    if (onInstall && !isInstalled && !isInstalling) {
      onInstall(plugin.id);
    }
  };

  const renderStars = (rating: number, size: 'sm' | 'md' | 'lg' = 'md') => {
    const starSize = size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';

    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`${starSize} ${
          i < Math.floor(rating)
            ? 'fill-yellow-400 text-yellow-400'
            : 'text-gray-300'
        }`}
      />
    ));
  };

  const getCompatibilityIcon = (compatibility: string) => {
    switch (compatibility.toLowerCase()) {
      case 'full':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'partial':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'none':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <CardTitle className="text-2xl font-bold">{plugin.name}</CardTitle>
                {plugin.featured && (
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    Destacado
                  </Badge>
                )}
                {plugin.verified && (
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    <Shield className="w-3 h-3 mr-1" />
                    Verificado
                  </Badge>
                )}
              </div>
              <CardDescription className="text-base mb-4">
                {plugin.description}
              </CardDescription>

              <div className="flex items-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <Avatar className="w-6 h-6">
                    <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${plugin.author}`} />
                    <AvatarFallback>
                      <User className="w-3 h-3" />
                    </AvatarFallback>
                  </Avatar>
                  <span>{plugin.author}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Badge variant="outline">v{plugin.version}</Badge>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span>
                    Actualizado {formatDistanceToNow(new Date(plugin.updatedAt), {
                      addSuffix: true,
                      locale: es
                    })}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsLiked(!isLiked)}
              >
                <Heart
                  className={`w-4 h-4 mr-1 ${
                    isLiked ? 'fill-red-500 text-red-500' : 'text-gray-400'
                  }`}
                />
                Favorito
              </Button>
              <Button
                onClick={handleInstall}
                disabled={isInstalled || isInstalling}
                size="lg"
              >
                {isInstalling ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Instalando...
                  </>
                ) : isInstalled ? (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Instalado
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Instalar Plugin
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="flex items-center gap-6 mb-4">
            <div className="flex items-center gap-2">
              {renderStars(plugin.rating, 'lg')}
              <span className="text-lg font-semibold ml-2">
                {plugin.rating.toFixed(1)}
              </span>
              <span className="text-gray-600">
                ({plugin.reviewCount} reseñas)
              </span>
            </div>
            <div className="flex items-center gap-1 text-gray-600">
              <Download className="w-4 h-4" />
              <span>{plugin.downloads.toLocaleString()} descargas</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Badge variant="secondary">{plugin.category}</Badge>
            {plugin.tags.map((tag) => (
              <Badge key={tag} variant="outline">
                {tag}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Vista General</TabsTrigger>
          <TabsTrigger value="reviews">Reseñas ({plugin.reviewCount})</TabsTrigger>
          <TabsTrigger value="compatibility">Compatibilidad</TabsTrigger>
          <TabsTrigger value="support">Soporte</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Screenshots */}
          {plugin.screenshots && plugin.screenshots.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Capturas de Pantalla</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {plugin.screenshots.map((screenshot, index) => (
                    <img
                      key={index}
                      src={screenshot}
                      alt={`Screenshot ${index + 1}`}
                      className="rounded-lg border shadow-sm hover:shadow-md transition-shadow"
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Long Description */}
          {plugin.longDescription && (
            <Card>
              <CardHeader>
                <CardTitle>Descripción Detallada</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose max-w-none">
                  {plugin.longDescription.split('\n').map((paragraph, index) => (
                    <p key={index} className="mb-4 text-gray-700">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Features */}
          {plugin.features && plugin.features.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Características</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {plugin.features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Requirements */}
          {plugin.requirements && plugin.requirements.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Requisitos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {plugin.requirements.map((requirement, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-blue-500 flex-shrink-0" />
                      <span className="text-sm">{requirement}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="reviews" className="space-y-6">
          {/* Review Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Resumen de Reseñas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold">{plugin.rating.toFixed(1)}</div>
                  <div className="flex justify-center mb-1">
                    {renderStars(plugin.rating)}
                  </div>
                  <div className="text-sm text-gray-600">
                    {plugin.reviewCount} reseñas
                  </div>
                </div>
                <Separator orientation="vertical" className="h-16" />
                <div className="flex-1">
                  <div className="space-y-1">
                    {[5, 4, 3, 2, 1].map((stars) => (
                      <div key={stars} className="flex items-center gap-2 text-sm">
                        <span className="w-3">{stars}</span>
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-yellow-400 h-2 rounded-full"
                            style={{ width: '60%' }}
                          ></div>
                        </div>
                        <span className="w-8 text-right">12</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Individual Reviews */}
          <div className="space-y-4">
            {reviews.map((review) => (
              <Card key={review.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <Avatar>
                      <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${review.userId}`} />
                      <AvatarFallback>
                        <User className="w-4 h-4" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium">{review.userName || 'Usuario Anónimo'}</span>
                        <div className="flex">
                          {renderStars(review.rating, 'sm')}
                        </div>
                        <span className="text-sm text-gray-500">
                          {formatDistanceToNow(new Date(review.createdAt), {
                            addSuffix: true,
                            locale: es
                          })}
                        </span>
                      </div>
                      {review.title && (
                        <h4 className="font-medium mb-2">{review.title}</h4>
                      )}
                      <p className="text-gray-700 mb-3">{review.comment}</p>
                      {review.pros && review.pros.length > 0 && (
                        <div className="mb-2">
                          <div className="flex items-center gap-1 text-green-600 text-sm mb-1">
                            <ThumbsUp className="w-3 h-3" />
                            <span>Pros:</span>
                          </div>
                          <ul className="text-sm text-gray-600 ml-4">
                            {review.pros.map((pro: string, index: number) => (
                              <li key={index}>• {pro}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {review.cons && review.cons.length > 0 && (
                        <div>
                          <div className="flex items-center gap-1 text-red-600 text-sm mb-1">
                            <ThumbsDown className="w-3 h-3" />
                            <span>Contras:</span>
                          </div>
                          <ul className="text-sm text-gray-600 ml-4">
                            {review.cons.map((con: string, index: number) => (
                              <li key={index}>• {con}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="compatibility" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Compatibilidad del Sistema</CardTitle>
              <CardDescription>
                Versiones de Proyecto Semilla compatibles con este plugin
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {plugin.compatibility?.map((version) => (
                  <div key={version} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-2">
                      {getCompatibilityIcon(version)}
                      <span>Proyecto Semilla {version}</span>
                    </div>
                    <Badge variant="secondary">
                      Compatible
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="support" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Información de Soporte</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {plugin.documentationUrl && (
                <div className="flex items-center gap-2">
                  <ExternalLink className="w-4 h-4 text-blue-500" />
                  <a
                    href={plugin.documentationUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Documentación Completa
                  </a>
                </div>
              )}

              {plugin.supportEmail && (
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-green-500" />
                  <a
                    href={`mailto:${plugin.supportEmail}`}
                    className="text-green-600 hover:underline"
                  >
                    Soporte por Email: {plugin.supportEmail}
                  </a>
                </div>
              )}

              {plugin.license && (
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-purple-500" />
                  <span>Licencia: {plugin.license}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};