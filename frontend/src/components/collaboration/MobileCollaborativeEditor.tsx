import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Edit3, Users, Save, Undo, Redo, Bold, Italic, Underline,
  AlignLeft, AlignCenter, AlignRight, List, Link, Image,
  Type, Palette, MoreHorizontal
} from 'lucide-react';
import { MobileGestureHandler } from './MobileGestureHandler';

interface MobileCollaborativeEditorProps {
  content: string;
  onContentChange: (content: string) => void;
  participants: Array<{
    id: string;
    name: string;
    avatar?: string;
    cursor?: { line: number; column: number };
    selection?: { start: number; end: number };
    color: string;
  }>;
  currentUser: {
    id: string;
    name: string;
    avatar?: string;
  };
  onSave?: () => void;
  onUndo?: () => void;
  onRedo?: () => void;
  isOnline?: boolean;
  lastSaved?: string;
}

export const MobileCollaborativeEditor: React.FC<MobileCollaborativeEditorProps> = ({
  content,
  onContentChange,
  participants,
  currentUser,
  onSave,
  onUndo,
  onRedo,
  isOnline = true,
  lastSaved
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showToolbar, setShowToolbar] = useState(false);
  const [cursorPosition, setCursorPosition] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleContentChange = (newContent: string) => {
    onContentChange(newContent);
  };

  const handleSave = () => {
    onSave?.();
  };

  const handleGesture = (gesture: string) => {
    switch (gesture) {
      case 'swipeLeft':
        // Next participant
        break;
      case 'swipeRight':
        // Previous participant
        break;
      case 'swipeUp':
        setShowToolbar(!showToolbar);
        break;
      case 'swipeDown':
        setIsEditing(!isEditing);
        break;
      case 'doubleTap':
        setIsEditing(true);
        break;
      case 'longPress':
        // Show context menu
        break;
    }
  };

  const formatText = (format: string) => {
    // Implement text formatting logic
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = content.substring(start, end);

    let formattedText = '';
    switch (format) {
      case 'bold':
        formattedText = `**${selectedText}**`;
        break;
      case 'italic':
        formattedText = `*${selectedText}*`;
        break;
      case 'underline':
        formattedText = `<u>${selectedText}</u>`;
        break;
      case 'list':
        formattedText = selectedText.split('\n').map(line => `- ${line}`).join('\n');
        break;
      default:
        return;
    }

    const newContent = content.substring(0, start) + formattedText + content.substring(end);
    onContentChange(newContent);
  };

  const renderCursors = () => {
    return participants
      .filter(p => p.cursor && p.id !== currentUser.id)
      .map(participant => (
        <div
          key={participant.id}
          className="absolute pointer-events-none z-10"
          style={{
            left: `${participant.cursor!.column * 8}px`,
            top: `${participant.cursor!.line * 20}px`,
          }}
        >
          <div
            className="w-0.5 h-5"
            style={{ backgroundColor: participant.color }}
          />
          <div
            className="px-2 py-1 rounded text-xs text-white text-nowrap"
            style={{ backgroundColor: participant.color }}
          >
            {participant.name}
          </div>
        </div>
      ));
  };

  const renderSelections = () => {
    return participants
      .filter(p => p.selection && p.id !== currentUser.id)
      .map(participant => (
        <div
          key={`selection-${participant.id}`}
          className="absolute pointer-events-none"
          style={{
            backgroundColor: `${participant.color}20`,
            left: `${participant.selection!.start * 8}px`,
            width: `${(participant.selection!.end - participant.selection!.start) * 8}px`,
            height: '20px'
          }}
        />
      ));
  };

  return (
    <MobileGestureHandler
      onSwipeLeft={() => handleGesture('swipeLeft')}
      onSwipeRight={() => handleGesture('swipeRight')}
      onSwipeUp={() => handleGesture('swipeUp')}
      onSwipeDown={() => handleGesture('swipeDown')}
      onDoubleTap={() => handleGesture('doubleTap')}
      onLongPress={() => handleGesture('longPress')}
      className="h-full"
    >
      <div className="h-full flex flex-col bg-white">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-3">
            <Edit3 className="w-5 h-5 text-blue-600" />
            <div>
              <h3 className="font-semibold">Editor Colaborativo</h3>
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {participants.slice(0, 3).map(participant => (
                    <Avatar key={participant.id} className="w-6 h-6 border-2 border-white">
                      <AvatarImage src={participant.avatar} />
                      <AvatarFallback className="text-xs">
                        {participant.name.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                  ))}
                  {participants.length > 3 && (
                    <div className="w-6 h-6 bg-gray-200 border-2 border-white rounded-full flex items-center justify-center">
                      <span className="text-xs text-gray-600">+{participants.length - 3}</span>
                    </div>
                  )}
                </div>
                <Badge variant="secondary" className="text-xs">
                  {participants.length} colaborando
                </Badge>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-xs text-gray-600">
              {isOnline ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
        </div>

        {/* Toolbar (Collapsible) */}
        {showToolbar && (
          <div className="border-b p-2 bg-gray-50">
            <div className="flex flex-wrap gap-1">
              <Button variant="ghost" size="sm" onClick={() => formatText('bold')}>
                <Bold className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => formatText('italic')}>
                <Italic className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => formatText('underline')}>
                <Underline className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={() => formatText('list')}>
                <List className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Link className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Image className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={onUndo}>
                <Undo className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={onRedo}>
                <Redo className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Editor */}
        <div className="flex-1 relative overflow-hidden">
          {renderSelections()}
          {renderCursors()}

          <Textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => handleContentChange(e.target.value)}
            onFocus={() => setIsEditing(true)}
            onBlur={() => setIsEditing(false)}
            onSelect={(e) => {
              const target = e.target as HTMLTextAreaElement;
              setCursorPosition(target.selectionStart);
            }}
            placeholder="Empieza a escribir... Los cambios se sincronizan en tiempo real."
            className="w-full h-full resize-none border-0 rounded-none focus:ring-0 p-4 text-base leading-relaxed"
            style={{
              fontFamily: 'system-ui, -apple-system, sans-serif',
              lineHeight: '1.6'
            }}
          />
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={() => setShowToolbar(!showToolbar)}>
                <MoreHorizontal className="w-4 h-4" />
              </Button>
              <span className="text-xs text-gray-600">
                {content.length} caracteres
              </span>
            </div>
            <div className="flex items-center gap-2">
              {lastSaved && (
                <span className="text-xs text-gray-600">
                  Guardado {new Date(lastSaved).toLocaleTimeString('es-ES', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              )}
              <Button onClick={handleSave} size="sm">
                <Save className="w-4 h-4 mr-1" />
                Guardar
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Instructions */}
        <div className="fixed bottom-20 left-4 right-4 bg-blue-50 border border-blue-200 rounded-lg p-3 md:hidden">
          <div className="flex items-start gap-2">
            <div className="text-blue-600 mt-0.5">
              <Edit3 className="w-4 h-4" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900">Gestos disponibles:</p>
              <ul className="text-xs text-blue-800 mt-1 space-y-1">
                <li>• Desliza arriba/abajo: alternar edición</li>
                <li>• Toca dos veces: activar edición</li>
                <li>• Mantén presionado: menú contextual</li>
                <li>• Pellizca: zoom del texto</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </MobileGestureHandler>
  );
};