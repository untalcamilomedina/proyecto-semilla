'use client';

import { useArticles, useArticleStats } from '../hooks/useArticles';
import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api-client';

export default function Home() {
  const [statusFilter, setStatusFilter] = useState<'draft' | 'published' | 'review'>('published');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginForm, setLoginForm] = useState({ email: 'demo@demo-company.com', password: 'demo123' });
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [showRegister, setShowRegister] = useState(false);
  const [registerForm, setRegisterForm] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    tenant_id: '8aa99184-4011-4cfc-b2cb-82b64f10d72b' // Demo company tenant
  });
  const [isRegistering, setIsRegistering] = useState(false);
  const [registerError, setRegisterError] = useState('');

  const { data: articles, isLoading, error } = useArticles(
    isAuthenticated ? { status_filter: statusFilter, limit: 10 } : undefined
  );
  const { data: stats } = useArticleStats();

  useEffect(() => {
    // Check if user is already authenticated
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoggingIn(true);
    setLoginError('');

    try {
      await apiClient.login({
        email: loginForm.email,
        password: loginForm.password
      });
      setIsAuthenticated(true);
    } catch (error: any) {
      setLoginError(error.detail || 'Login failed');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsRegistering(true);
    setRegisterError('');

    try {
      // First register the user
      await apiClient.register(registerForm);
      
      // Then automatically log them in
      await apiClient.login({
        email: registerForm.email,
        password: registerForm.password
      });
      
      setIsAuthenticated(true);
      setShowRegister(false);
    } catch (error: any) {
      setRegisterError(error.detail || 'Registration failed');
    } finally {
      setIsRegistering(false);
    }
  };

  const handleLogout = () => {
    apiClient.logout();
    setIsAuthenticated(false);
    setLoginForm({ email: 'demo@demo-company.com', password: 'demo123' });
    setShowRegister(false);
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
                <strong>Email:</strong> demo@demo-company.com<br />
                <strong>Contraseña:</strong> demo123
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
  if (typeof window !== 'undefined') {
    window.location.href = '/dashboard';
  }

  return null;
}