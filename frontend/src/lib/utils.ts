// Input validation utilities

export interface ValidationResult {
  isValid: boolean;
  error?: string;
  sanitized?: string;
}

export const inputValidation = {
  // Email validation
  validateEmail: (email: string): ValidationResult & { sanitized: string } => {
    if (!email || typeof email !== 'string') {
      return { isValid: false, error: 'Email es requerido', sanitized: '' };
    }

    const trimmed = email.trim().toLowerCase();

    if (trimmed.length === 0) {
      return { isValid: false, error: 'Email es requerido', sanitized: '' };
    }

    // Basic email regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmed)) {
      return { isValid: false, error: 'Formato de email inválido', sanitized: trimmed };
    }

    if (trimmed.length > 254) {
      return { isValid: false, error: 'Email demasiado largo', sanitized: trimmed };
    }

    return { isValid: true, sanitized: trimmed };
  },

  // Username validation (for first_name and last_name)
  validateUsername: (name: string): ValidationResult & { sanitized: string } => {
    if (!name || typeof name !== 'string') {
      return { isValid: false, error: 'Nombre es requerido', sanitized: '' };
    }

    const trimmed = name.trim();

    if (trimmed.length === 0) {
      return { isValid: false, error: 'Nombre es requerido', sanitized: '' };
    }

    if (trimmed.length < 2) {
      return { isValid: false, error: 'Nombre debe tener al menos 2 caracteres', sanitized: trimmed };
    }

    if (trimmed.length > 50) {
      return { isValid: false, error: 'Nombre demasiado largo', sanitized: trimmed };
    }

    // Only allow letters, spaces, hyphens, and apostrophes
    const nameRegex = /^[a-zA-ZÀ-ÿ\s\-']+$/;
    if (!nameRegex.test(trimmed)) {
      return { isValid: false, error: 'Nombre contiene caracteres inválidos', sanitized: trimmed };
    }

    return { isValid: true, sanitized: trimmed };
  },

  // Password validation
  validatePassword: (password: string): ValidationResult & { errors: string[] } => {
    const errors: string[] = [];

    if (!password || typeof password !== 'string') {
      return { isValid: false, errors: ['Contraseña es requerida'] };
    }

    if (password.length < 8) {
      errors.push('Contraseña debe tener al menos 8 caracteres');
    }

    if (password.length > 128) {
      errors.push('Contraseña demasiado larga');
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('Contraseña debe contener al menos una letra mayúscula');
    }

    if (!/[a-z]/.test(password)) {
      errors.push('Contraseña debe contener al menos una letra minúscula');
    }

    if (!/\d/.test(password)) {
      errors.push('Contraseña debe contener al menos un número');
    }

    if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)) {
      errors.push('Contraseña debe contener al menos un carácter especial');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  },

  // Generic sanitization
  sanitizeString: (input: string, maxLength: number = 1000): string => {
    if (!input || typeof input !== 'string') {
      return '';
    }

    return input
      .trim()
      .replace(/[<>]/g, '') // Remove potential XSS characters
      .substring(0, maxLength);
  },

  // URL validation
  validateUrl: (url: string): ValidationResult & { sanitized: string } => {
    if (!url || typeof url !== 'string') {
      return { isValid: false, error: 'URL es requerida', sanitized: '' };
    }

    const trimmed = url.trim();

    if (trimmed.length === 0) {
      return { isValid: false, error: 'URL es requerida', sanitized: '' };
    }

    try {
      const urlObj = new URL(trimmed);
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        return { isValid: false, error: 'URL debe usar HTTP o HTTPS', sanitized: trimmed };
      }
      return { isValid: true, sanitized: trimmed };
    } catch {
      return { isValid: false, error: 'Formato de URL inválido', sanitized: trimmed };
    }
  }
};

// Other utility functions
export const formatDate = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatDateTime = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
};

export const generateId = (): string => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};

// ClassName utility function (commonly used in shadcn/ui components)
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
