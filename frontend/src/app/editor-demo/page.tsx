'use client';

import { useState } from 'react';
import { RichTextEditor } from '@/components/editor/RichTextEditor';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function EditorDemo() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isPreview, setIsPreview] = useState(false);

  const handleSave = () => {
    console.log('Guardando artículo:', { title, content });
    // Aquí iría la lógica para guardar en el backend
  };

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Editor WYSIWYG Demo
        </h1>
        <p className="text-gray-600">
          Prueba el editor de texto enriquecido con todas las funcionalidades
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Crear Artículo</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Título */}
          <div>
            <Label htmlFor="title">Título del Artículo</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Escribe el título de tu artículo..."
              className="mt-1"
            />
          </div>

          {/* Controles */}
          <div className="flex gap-2">
            <Button
              variant={isPreview ? "outline" : "default"}
              onClick={() => setIsPreview(false)}
            >
              Editar
            </Button>
            <Button
              variant={isPreview ? "default" : "outline"}
              onClick={() => setIsPreview(true)}
            >
              Vista Previa
            </Button>
            <Button onClick={handleSave} className="ml-auto">
              Guardar Artículo
            </Button>
          </div>

          {/* Editor o Preview */}
          {!isPreview ? (
            <div>
              <Label>Contenido</Label>
              <RichTextEditor
                content={content}
                onChange={setContent}
                placeholder="Escribe el contenido de tu artículo aquí..."
                className="mt-1"
              />
            </div>
          ) : (
            <div>
              <Label>Vista Previa</Label>
              <div className="mt-1 border rounded-lg p-4 min-h-[200px] bg-white">
                <h2 className="text-2xl font-bold mb-4">{title || 'Sin título'}</h2>
                <div 
                  className="prose prose-sm sm:prose lg:prose-lg xl:prose-2xl max-w-none"
                  dangerouslySetInnerHTML={{ __html: content || '<p class="text-gray-500">No hay contenido para mostrar...</p>' }}
                />
              </div>
            </div>
          )}

          {/* Información adicional */}
          <div className="text-sm text-gray-500 space-y-1">
            <p>• Usa la barra de herramientas para formatear el texto</p>
            <p>• Puedes agregar enlaces e imágenes</p>
            <p>• Usa Ctrl+Z para deshacer y Ctrl+Y para rehacer</p>
            <p>• El contenido se guarda automáticamente mientras escribes</p>
          </div>
        </CardContent>
      </Card>

      {/* Debug info */}
      {process.env.NODE_ENV === 'development' && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-sm">Debug Info</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-xs">
              <div>
                <strong>Título:</strong> {title}
              </div>
              <div>
                <strong>Contenido HTML:</strong>
                <pre className="mt-1 p-2 bg-gray-100 rounded text-xs overflow-auto max-h-32">
                  {content}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
