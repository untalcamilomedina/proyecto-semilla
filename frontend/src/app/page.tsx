'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { apiClient } from '@/lib/api-client';
import { UserRegister } from '@/types/api';

export default function HomePage() {
  console.log('🏠 HomePage component rendered');

  const router = useRouter();
  const { login, register, isAuthenticated, isLoading, error, clearError } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [needsSetup, setNeedsSetup] = useState<boolean | null>(null); // null = loading, true = needs setup, false = configured
  const [setupLoading, setSetupLoading] = useState(true);
  const [authInitialized, setAuthInitialized] = useState(false);

  useEffect(() => {
    console.log('🔐 Estado de autenticación:', { isAuthenticated, isLoading, authInitialized });
    // Only redirect if auth is initialized and user is authenticated
    if (authInitialized && isAuthenticated && !isLoading) {
      console.log('🔄 Redirigiendo a dashboard...');
      router.replace('/dashboard');
    }
  }, [isAuthenticated, isLoading, authInitialized, router]);

  useEffect(() => {
    // Mark auth as initialized when loading is complete
    if (!isLoading && !authInitialized) {
      console.log('✅ Autenticación inicializada');
      setAuthInitialized(true);
    }
  }, [isLoading, authInitialized]);

  useEffect(() => {
    // Check if system needs initial setup immediately
    const checkSetupStatus = async () => {
      console.log('🔍 Iniciando verificación de setup status...');

      try {
        console.log('📡 Llamando a apiClient.getSetupStatus()...');
        const status = await apiClient.getSetupStatus();
        console.log('✅ Setup status recibido:', status);
        setNeedsSetup(status.needs_setup);
      } catch (error) {
        console.error('❌ Error checking setup status:', error);
        // On error, assume system is already configured (safer default)
        console.log('⚠️ Error al verificar setup status, asumiendo sistema configurado');
        setNeedsSetup(false);
      } finally {
        setSetupLoading(false);
      }
    };

    // Execute immediately without delay
    checkSetupStatus();

    // Fallback: if it takes too long, assume system is configured
    const timeout = setTimeout(() => {
      if (setupLoading) {
        console.log('⏰ Timeout: asumiendo que el sistema está configurado');
        setNeedsSetup(false);
        setSetupLoading(false);
      }
    }, 5000); // 5 seconds timeout

    return () => clearTimeout(timeout);
  }, []);

  useEffect(() => {
    // Clear errors when component unmounts or on new login attempt
    return () => {
      clearError();
    };
  }, [clearError]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    try {
      await login(email, password);
      // The useEffect above will handle the redirect
    } catch (err) {
      // Error is already set in the store, just log it for debugging
      console.error('Login failed', err);
    }
  };

  const validatePassword = (password: string): string | null => {
    if (password.length < 8) {
      return 'La contraseña debe tener al menos 8 caracteres';
    }
    if (!/[A-Z]/.test(password)) {
      return 'La contraseña debe contener al menos una letra mayúscula';
    }
    if (!/[a-z]/.test(password)) {
      return 'La contraseña debe contener al menos una letra minúscula';
    }
    if (!/\d/.test(password)) {
      return 'La contraseña debe contener al menos un número';
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      return 'La contraseña debe contener al menos un carácter especial';
    }
    return null;
  };

  const handleSetup = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setPasswordError('');

    console.log('🚀 Iniciando proceso de registro...');
    console.log('📝 Datos del formulario:', { email, firstName, lastName, passwordLength: password.length });

    // Validate password
    const passwordValidationError = validatePassword(password);
    if (passwordValidationError) {
      console.log('❌ Error de validación de contraseña:', passwordValidationError);
      setPasswordError(passwordValidationError);
      return;
    }

    console.log('✅ Validación de contraseña exitosa');

    try {
      const userData: UserRegister = {
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        // tenant_id is optional and will be handled by backend
      };

      console.log('📡 Enviando datos de registro al backend:', { ...userData, password: '[REDACTED]' });
      await register(userData);

      // Success! The useEffect above will handle the redirect to dashboard
      console.log('✅ Superadministrador creado exitosamente');
    } catch (err: any) {
      console.error('❌ Error en el registro:', err);

      // Log detailed error information
      if (err?.response) {
        console.error('📋 Respuesta del servidor:', {
          status: err.response.status,
          statusText: err.response.statusText,
          data: err.response.data,
          headers: err.response.headers
        });
      } else if (err?.request) {
        console.error('📡 Error de red - no se recibió respuesta:', err.request);
      } else {
        console.error('⚙️ Error de configuración:', err.message);
      }

      // Also set a more user-friendly error if the store error is not clear
      if (!error && err?.response?.data?.detail) {
        console.error('Setting fallback error:', err.response.data.detail);
      }
    }
  };

  // Show loading while checking setup status
  if (setupLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Verificando configuración del sistema...</p>
          <p className="text-sm text-gray-500 mt-2">Si tarda demasiado, se mostrará el formulario de login</p>
          {/* Force show setup wizard after 5 seconds */}
          <script dangerouslySetInnerHTML={{
            __html: `
              setTimeout(() => {
                const loadingElement = document.querySelector('.animate-spin');
                if (loadingElement) {
                  window.location.reload();
                }
              }, 5000);
            `
          }} />
        </div>
      </div>
    );
  }

  // Show setup form if system needs initial setup
  if (needsSetup === true) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="w-full max-w-lg p-8 space-y-8 bg-white rounded-xl shadow-2xl border border-gray-200">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl">🌱</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">¡Bienvenido a Proyecto Semilla!</h1>
            <p className="text-gray-600 text-lg">
              La primera plataforma SaaS Vibecoding-native del mundo
            </p>
            <p className="mt-4 text-sm text-gray-500">
              Solo necesitamos crear tu cuenta de superadministrador para comenzar
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSetup}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="firstName" className="text-sm font-medium text-gray-700">Nombre</label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  autoComplete="given-name"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>

              <div>
                <label htmlFor="lastName" className="text-sm font-medium text-gray-700">Apellido</label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  autoComplete="family-name"
                  required
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="text-sm font-medium text-gray-700">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>

            <div>
              <label htmlFor="password" className="text-sm font-medium text-gray-700">Contraseña</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setPasswordError(''); // Clear password error on change
                }}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                  passwordError ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300'
                }`}
              />
              {passwordError && (
                <p className="mt-1 text-sm text-red-600">{passwordError}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial.
              </p>
            </div>

            {error && (
              <div className="p-3 text-sm text-red-700 bg-red-100 rounded-md">
                {error}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-3 px-6 border border-transparent rounded-lg shadow-lg text-base font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transform transition hover:scale-105"
              >
                {isLoading ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Configurando tu plataforma...
                  </div>
                ) : (
                  <div className="flex items-center">
                    <span className="mr-2">🚀</span>
                    Comenzar mi viaje Vibecoding
                  </div>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Show login form if system is already configured
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center text-gray-900">Iniciar Sesión</h1>

        <form className="space-y-6" onSubmit={handleLogin}>
          <div>
            <label htmlFor="email" className="text-sm font-medium text-gray-700">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>

          <div>
            <label htmlFor="password" className="text-sm font-medium text-gray-700">Contraseña</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>

          {error && (
            <div className="p-3 text-sm text-red-700 bg-red-100 rounded-md">
              {error}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
