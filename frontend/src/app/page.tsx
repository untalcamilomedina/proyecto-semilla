'use client';

import { useArticles, useArticleStats } from '../hooks/useArticles';
import { useState } from 'react';

export default function Home() {
  const [statusFilter, setStatusFilter] = useState<'draft' | 'published' | 'review'>('published');
  const { data: articles, isLoading, error } = useArticles({ status_filter: statusFilter, limit: 10 });
  const { data: stats } = useArticleStats();

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
        <div className="text-red-500">Error loading articles: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Proyecto Semilla CMS</h1>
          <p className="text-gray-600 mt-2">Multi-tenant SaaS platform dashboard</p>
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