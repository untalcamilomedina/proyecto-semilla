'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function LoginComponent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    // Mostrar mensaje de éxito si viene del registro
    if (searchParams?.get('registered') === 'true') {
      setSuccessMessage('¡Registro exitoso! Ahora puedes iniciar sesión.');
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7777'}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
        credentials: 'include',
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Credenciales inválidas');
      }

      // Store auth data in Zustand store

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ocurrió un error inesperado');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md">
      <form className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Iniciar Sesión
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Ingresa a tu cuenta de Proyecto Semilla
          </p>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {successMessage}
          </div>
        )}
        
        <div className="space-y-4">
          <div>
            <label 
              htmlFor="email" 
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="usuario@ejemplo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            />
          </div>
          
          <div>
            <label 
              htmlFor="password" 
              className="block text-sm font-medium text-gray-700"
            >
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={loading}
            />
          </div>
        </div>
        
        <div>
          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </div>

        <div className="text-sm text-center">
          <span className="text-gray-600">¿No tienes cuenta? </span>
          <a
            href="/register"
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            Regístrate aquí
          </a>
        </div>

        {/* Test credentials hint for development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-3 bg-gray-100 rounded text-xs text-gray-600">
            <p className="font-semibold">Credenciales de prueba:</p>
            <p>Email: demo@demo-company.com</p>
            <p>Password: demo123</p>
            <p className="mt-1 text-gray-500">O crea una cuenta nueva con el registro</p>
          </div>
        )}
      </form>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginComponent />
    </Suspense>
  );
}