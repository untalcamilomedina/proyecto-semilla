import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  MessageCircle, Users, Send, Mic, MicOff, Video, VideoOff,
  Phone, PhoneOff, MoreVertical, Smile, Paperclip, X,
  ChevronUp, ChevronDown, Maximize, Minimize
} from 'lucide-react';

interface MobileCollaborationPanelProps {
  roomId: string;
  currentUser: {
    id: string;
    name: string;
    avatar?: string;
  };
  participants: Array<{
    id: string;
    name: string;
    avatar?: string;
    isOnline: boolean;
    isTyping?: boolean;
    lastSeen?: string;
  }>;
  messages: Array<{
    id: string;
    userId: string;
    userName: string;
    content: string;
    timestamp: string;
    type: 'text' | 'system' | 'file';
    reactions?: Array<{ emoji: string; count: number; users: string[] }>;
  }>;
  onSendMessage: (content: string) => void;
  onToggleAudio?: () => void;
  onToggleVideo?: () => void;
  onLeaveRoom?: () => void;
  isAudioEnabled?: boolean;
  isVideoEnabled?: boolean;
  isMinimized?: boolean;
  onToggleMinimize?: () => void;
}

export const MobileCollaborationPanel: React.FC<MobileCollaborationPanelProps> = ({
  roomId,
  currentUser,
  participants,
  messages,
  onSendMessage,
  onToggleAudio,
  onToggleVideo,
  onLeaveRoom,
  isAudioEnabled = false,
  isVideoEnabled = false,
  isMinimized = false,
  onToggleMinimize
}) => {
  const [messageInput, setMessageInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showParticipants, setShowParticipants] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      onSendMessage(messageInput.trim());
      setMessageInput('');
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleInputChange = (value: string) => {
    setMessageInput(value);
    // Simulate typing indicator
    if (value && !isTyping) {
      setIsTyping(true);
    } else if (!value && isTyping) {
      setIsTyping(false);
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Card className="w-16 h-16 shadow-lg border-2">
          <CardContent className="p-0 flex items-center justify-center h-full">
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleMinimize}
              className="w-full h-full"
            >
              <MessageCircle className="w-6 h-6" />
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-white flex flex-col md:hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-blue-50">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleMinimize}
            className="md:hidden"
          >
            <Minimize className="w-4 h-4" />
          </Button>
          <div>
            <h3 className="font-semibold text-lg">Colaboración</h3>
            <p className="text-sm text-gray-600">
              {participants.length} participante{participants.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowParticipants(!showParticipants)}
          >
            <Users className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onLeaveRoom}
            className="text-red-600"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Participants Panel (Collapsible) */}
      {showParticipants && (
        <div className="border-b bg-gray-50 p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium">Participantes</h4>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowParticipants(false)}
            >
              <ChevronUp className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {participants.map(participant => (
              <div key={participant.id} className="flex items-center gap-3">
                <div className="relative">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={participant.avatar} />
                    <AvatarFallback>
                      {getInitials(participant.name)}
                    </AvatarFallback>
                  </Avatar>
                  {participant.isOnline && (
                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{participant.name}</p>
                  {participant.isTyping && (
                    <p className="text-xs text-blue-600">Escribiendo...</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Voice/Video Controls */}
      <div className="flex items-center justify-center gap-4 p-3 border-b bg-green-50">
        <Button
          variant={isAudioEnabled ? "default" : "destructive"}
          size="sm"
          onClick={onToggleAudio}
          className="rounded-full w-12 h-12"
        >
          {isAudioEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
        </Button>
        <Button
          variant={isVideoEnabled ? "default" : "secondary"}
          size="sm"
          onClick={onToggleVideo}
          className="rounded-full w-12 h-12"
        >
          {isVideoEnabled ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={onLeaveRoom}
          className="rounded-full w-12 h-12 text-red-600 border-red-600"
        >
          <PhoneOff className="w-4 h-4" />
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map(message => (
            <div key={message.id} className="flex gap-3">
              <Avatar className="w-8 h-8 flex-shrink-0">
                <AvatarImage src={participants.find(p => p.id === message.userId)?.avatar} />
                <AvatarFallback>
                  {getInitials(message.userName)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-sm">{message.userName}</span>
                  <span className="text-xs text-gray-500">
                    {formatTime(message.timestamp)}
                  </span>
                </div>
                <div className="bg-gray-100 rounded-lg px-3 py-2">
                  <p className="text-sm">{message.content}</p>
                </div>
                {message.reactions && message.reactions.length > 0 && (
                  <div className="flex gap-1 mt-1">
                    {message.reactions.map((reaction, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {reaction.emoji} {reaction.count}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Message Input */}
      <div className="border-t p-4 bg-white">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
          >
            <Smile className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Paperclip className="w-4 h-4" />
          </Button>
          <Input
            ref={inputRef}
            placeholder="Escribe un mensaje..."
            value={messageInput}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!messageInput.trim()}
            size="sm"
            className="rounded-full w-10 h-10 p-0"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>

        {/* Emoji Picker (Collapsible) */}
        {showEmojiPicker && (
          <div className="mt-3 p-3 border rounded-lg bg-gray-50">
            <div className="grid grid-cols-8 gap-2">
              {['😀', '😂', '❤️', '👍', '👎', '🎉', '🔥', '💯'].map(emoji => (
                <Button
                  key={emoji}
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setMessageInput(prev => prev + emoji);
                    setShowEmojiPicker(false);
                  }}
                  className="w-8 h-8 p-0 text-lg"
                >
                  {emoji}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};