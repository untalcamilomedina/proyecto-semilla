import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Star, Download, Heart, ExternalLink, Calendar, User } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface PluginCardProps {
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
  };
  onInstall?: (pluginId: string) => void;
  onViewDetails?: (pluginId: string) => void;
  isInstalled?: boolean;
  isInstalling?: boolean;
}

export const PluginCard: React.FC<PluginCardProps> = ({
  plugin,
  onInstall,
  onViewDetails,
  isInstalled = false,
  isInstalling = false
}) => {
  const [isLiked, setIsLiked] = useState(false);

  const handleInstall = () => {
    if (onInstall && !isInstalled && !isInstalling) {
      onInstall(plugin.id);
    }
  };

  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(plugin.id);
    }
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${
          i < Math.floor(rating)
            ? 'fill-yellow-400 text-yellow-400'
            : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <Card className="h-full hover:shadow-lg transition-shadow duration-200 border-2 hover:border-blue-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <CardTitle className="text-lg font-semibold truncate">
                {plugin.name}
              </CardTitle>
              {plugin.featured && (
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                  Destacado
                </Badge>
              )}
              {plugin.verified && (
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Verificado
                </Badge>
              )}
            </div>
            <CardDescription className="text-sm text-gray-600 line-clamp-2">
              {plugin.description}
            </CardDescription>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsLiked(!isLiked)}
            className="ml-2"
          >
            <Heart
              className={`w-4 h-4 ${
                isLiked ? 'fill-red-500 text-red-500' : 'text-gray-400'
              }`}
            />
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex items-center gap-4 mb-3">
          <div className="flex items-center gap-1">
            <Avatar className="w-6 h-6">
              <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${plugin.author}`} />
              <AvatarFallback>
                <User className="w-3 h-3" />
              </AvatarFallback>
            </Avatar>
            <span className="text-sm text-gray-600">{plugin.author}</span>
          </div>
          <Badge variant="outline" className="text-xs">
            v{plugin.version}
          </Badge>
        </div>

        <div className="flex items-center gap-4 mb-3">
          <div className="flex items-center gap-1">
            {renderStars(plugin.rating)}
            <span className="text-sm text-gray-600 ml-1">
              {plugin.rating.toFixed(1)} ({plugin.reviewCount})
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
          <div className="flex items-center gap-1">
            <Download className="w-4 h-4" />
            <span>{plugin.downloads.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            <span>
              {formatDistanceToNow(new Date(plugin.updatedAt), {
                addSuffix: true,
                locale: es
              })}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          <Badge variant="secondary" className="text-xs">
            {plugin.category}
          </Badge>
          {plugin.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
          {plugin.tags.length > 2 && (
            <Badge variant="outline" className="text-xs">
              +{plugin.tags.length - 2}
            </Badge>
          )}
        </div>
      </CardContent>

      <CardFooter className="pt-0">
        <div className="flex gap-2 w-full">
          <Button
            variant="outline"
            size="sm"
            onClick={handleViewDetails}
            className="flex-1"
          >
            <ExternalLink className="w-4 h-4 mr-1" />
            Ver Detalles
          </Button>
          <Button
            onClick={handleInstall}
            disabled={isInstalled || isInstalling}
            size="sm"
            className="flex-1"
          >
            {isInstalling ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-1" />
                Instalando...
              </>
            ) : isInstalled ? (
              'Instalado'
            ) : (
              <>
                <Download className="w-4 h-4 mr-1" />
                Instalar
              </>
            )}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};