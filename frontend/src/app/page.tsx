'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '../lib/api-client';
import { inputValidation } from '../lib/utils';

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginForm, setLoginForm] = useState({
    email: process.env.NEXT_PUBLIC_DEMO_EMAIL || 'demo@demo-company.com',
    password: process.env.NEXT_PUBLIC_DEMO_PASSWORD || 'demo123'
  });
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [showRegister, setShowRegister] = useState(false);
  const [registerForm, setRegisterForm] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    tenant_id: process.env.NEXT_PUBLIC_DEFAULT_TENANT_ID || ''
  });
  const [isRegistering, setIsRegistering] = useState(false);
  const [registerError, setRegisterError] = useState('');

  useEffect(() => {
    // Check if user is already authenticated by checking cookies
    const checkAuth = async () => {
      try {
        // Try to get current user info - if successful, user is authenticated
        await apiClient.getCurrentUser();
        setIsAuthenticated(true);
      } catch (error) {
        // User is not authenticated
        setIsAuthenticated(false);
      }
    };

    if (typeof window !== 'undefined') {
      checkAuth();
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoggingIn(true);
    setLoginError('');

    // Validar email antes de enviar
    const emailValidation = inputValidation.validateEmail(loginForm.email);
    if (!emailValidation.isValid) {
      setLoginError(emailValidation.error || 'Email inválido');
      setIsLoggingIn(false);
      return;
    }

    // Validar que la contraseña no esté vacía
    if (!loginForm.password.trim()) {
      setLoginError('Contraseña es requerida');
      setIsLoggingIn(false);
      return;
    }

    try {
      console.log('Intentando login con:', { email: emailValidation.sanitized });
      await apiClient.login({
        email: emailValidation.sanitized,
        password: loginForm.password
      });
      console.log('Login exitoso, configurando autenticación');
      setIsAuthenticated(true);
    } catch (error: any) {
      console.error('Error en login:', error);
      const errorMessage = error.response?.data?.detail ||
                          error.detail ||
                          error.message ||
                          'Error de conexión con el servidor';
      setLoginError(errorMessage);
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsRegistering(true);
    setRegisterError('');

    // Validaciones de entrada
    const emailValidation = inputValidation.validateEmail(registerForm.email);
    if (!emailValidation.isValid) {
      setRegisterError(emailValidation.error || 'Email inválido');
      setIsRegistering(false);
      return;
    }

    const firstNameValidation = inputValidation.validateUsername(registerForm.first_name);
    if (!firstNameValidation.isValid) {
      setRegisterError(firstNameValidation.error || 'Nombre inválido');
      setIsRegistering(false);
      return;
    }

    const lastNameValidation = inputValidation.validateUsername(registerForm.last_name);
    if (!lastNameValidation.isValid) {
      setRegisterError(lastNameValidation.error || 'Apellido inválido');
      setIsRegistering(false);
      return;
    }

    const passwordValidation = inputValidation.validatePassword(registerForm.password);
    if (!passwordValidation.isValid) {
      setRegisterError(passwordValidation.errors.join('. '));
      setIsRegistering(false);
      return;
    }

    try {
      // Registrar al usuario con datos sanitizados
      const sanitizedData: any = {
        email: emailValidation.sanitized,
        first_name: firstNameValidation.sanitized,
        last_name: lastNameValidation.sanitized,
        password: registerForm.password
      };

      // Solo incluir tenant_id si tiene un valor
      if (registerForm.tenant_id.trim()) {
        sanitizedData.tenant_id = registerForm.tenant_id;
      }

      await apiClient.register(sanitizedData);

      // Iniciar sesión automáticamente
      await apiClient.login({
        email: emailValidation.sanitized,
        password: registerForm.password
      });

      setIsAuthenticated(true);
      setShowRegister(false);
    } catch (error: any) {
      setRegisterError(error.detail || 'Error en el registro');
    } finally {
      setIsRegistering(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsAuthenticated(false);
      setLoginForm({
        email: process.env.NEXT_PUBLIC_DEMO_EMAIL || 'demo@demo-company.com',
        password: process.env.NEXT_PUBLIC_DEMO_PASSWORD || 'demo123'
      });
      setShowRegister(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Proyecto Semilla 🌱
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Plataforma Vibecoding-native para desarrollo empresarial
            </p>
            <p className="mt-2 text-center text-xs text-gray-500">
              Crea módulos empresariales conversando con IA
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={handleLogin}>
            <div className="rounded-md shadow-sm -space-y-px">
              <div>
                <label htmlFor="email" className="sr-only">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Email"
                  value={loginForm.email}
                  onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                />
              </div>
              <div>
                <label htmlFor="password" className="sr-only">
                  Contraseña
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Contraseña"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                />
              </div>
            </div>

            {loginError && (
              <div className="text-red-600 text-sm text-center">
                {loginError}
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoggingIn}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {isLoggingIn ? 'Iniciando sesión...' : 'Iniciar Sesión'}
              </button>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                Credenciales de demo:<br />
                <strong>Email:</strong> {process.env.NEXT_PUBLIC_DEMO_EMAIL || 'demo@demo-company.com'}<br />
                <strong>Contraseña:</strong> {process.env.NEXT_PUBLIC_DEMO_PASSWORD || 'demo123'}
              </p>
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => setShowRegister(true)}
                  className="text-blue-600 hover:text-blue-500 text-sm"
                >
                  ¿No tienes cuenta? Regístrate aquí
                </button>
              </div>
            </div>
          </form>

          {/* Register Modal */}
          {showRegister && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white p-8 rounded-lg max-w-md w-full mx-4">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Crear Nueva Cuenta</h3>

                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                        Nombre
                      </label>
                      <input
                        id="first_name"
                        name="first_name"
                        type="text"
                        required
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={registerForm.first_name}
                        onChange={(e) => setRegisterForm({ ...registerForm, first_name: e.target.value })}
                      />
                    </div>
                    <div>
                      <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                        Apellido
                      </label>
                      <input
                        id="last_name"
                        name="last_name"
                        type="text"
                        required
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        value={registerForm.last_name}
                        onChange={(e) => setRegisterForm({ ...registerForm, last_name: e.target.value })}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="register_email" className="block text-sm font-medium text-gray-700">
                      Email
                    </label>
                    <input
                      id="register_email"
                      name="register_email"
                      type="email"
                      required
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      value={registerForm.email}
                      onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                    />
                  </div>

                  <div>
                    <label htmlFor="register_password" className="block text-sm font-medium text-gray-700">
                      Contraseña
                    </label>
                    <input
                      id="register_password"
                      name="register_password"
                      type="password"
                      required
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      value={registerForm.password}
                      onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                    />
                  </div>

                  {registerError && (
                    <div className="text-red-600 text-sm">
                      {registerError}
                    </div>
                  )}

                  <div className="flex space-x-4">
                    <button
                      type="button"
                      onClick={() => setShowRegister(false)}
                      className="flex-1 py-2 px-4 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                    >
                      Cancelar
                    </button>
                    <button
                      type="submit"
                      disabled={isRegistering}
                      className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      {isRegistering ? 'Creando cuenta...' : 'Registrarse'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Redirect to dashboard if authenticated
  useEffect(() => {
    if (isAuthenticated && typeof window !== 'undefined') {
      // Small delay to show the redirect message
      const timer = setTimeout(() => {
        router.push('/dashboard');
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [isAuthenticated, router]);

  // Show redirect screen if authenticated
  if (isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirigiendo al dashboard...</p>
        </div>
      </div>
    );
  }

  // This should never be reached, but just in case
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <p className="text-red-600">Error: Estado de autenticación inválido</p>
      </div>
    </div>
  );
}