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

  const handleLogout = () => {
    apiClient.logout();
    setIsAuthenticated(false);
    setLoginForm({ email: 'demo@demo-company.com', password: 'demo123' });
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
            </div>
          </form>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading articles...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500 text-center">
          <div>Error loading articles: {error.message}</div>
          <button
            onClick={handleLogout}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Cerrar Sesión
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Proyecto Semilla 🌱</h1>
            <p className="text-gray-600 mt-2">Plataforma Vibecoding-native para desarrollo empresarial</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Cerrar Sesión
          </button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Total Articles</h3>
              <p className="text-3xl font-bold text-blue-600">{stats.total_articles}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Published</h3>
              <p className="text-3xl font-bold text-green-600">{stats.published_articles}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Draft</h3>
              <p className="text-3xl font-bold text-yellow-600">{stats.draft_articles}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900">Total Views</h3>
              <p className="text-3xl font-bold text-purple-600">{stats.total_views}</p>
            </div>
          </div>
        )}

        {/* Filter Controls */}
        <div className="mb-6">
          <div className="flex space-x-4">
            <button
              onClick={() => setStatusFilter('published')}
              className={`px-4 py-2 rounded ${
                statusFilter === 'published'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Published
            </button>
            <button
              onClick={() => setStatusFilter('draft')}
              className={`px-4 py-2 rounded ${
                statusFilter === 'draft'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Draft
            </button>
            <button
              onClick={() => setStatusFilter('review')}
              className={`px-4 py-2 rounded ${
                statusFilter === 'review'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Review
            </button>
          </div>
        </div>

        {/* Articles List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Articles ({statusFilter})
            </h2>
          </div>
          <div className="divide-y divide-gray-200">
            {articles && articles.length > 0 ? (
              articles.map((article) => (
                <div key={article.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">
                        {article.title}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {article.excerpt}
                      </p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span>By {article.author_name}</span>
                        <span>•</span>
                        <span>{new Date(article.created_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{article.view_count} views</span>
                        <span>•</span>
                        <span className={`px-2 py-1 rounded text-xs ${
                          article.status === 'published'
                            ? 'bg-green-100 text-green-800'
                            : article.status === 'draft'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {article.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center text-gray-500">
                No articles found for status: {statusFilter}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}