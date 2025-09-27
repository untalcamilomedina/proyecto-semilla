'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import { Users, FileText, Activity, AlertTriangle, TrendingUp, RefreshCw } from 'lucide-react';

interface MetricDataPoint {
  date: string;
  value: number;
  bucket_start: string;
  bucket_end: string;
}

interface MetricData {
  name: string;
  data: MetricDataPoint[];
  total: number;
  average: number;
  trend: string;
}

interface RealtimeMetrics {
  active_users_24h: number;
  events_last_24h: number;
  errors_last_24h: number;
  timestamp: string;
}

interface AnalyticsSummary {
  tenant_id: string;
  period_days: number;
  summary: Record<string, {
    total: number;
    average: number;
    trend: string;
    data_points: number;
  }>;
}

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [realtimeMetrics, setRealtimeMetrics] = useState<RealtimeMetrics | null>(null);
  const [metricsData, setMetricsData] = useState<Record<string, MetricDataPoint[]> | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadAnalyticsData = async () => {
    try {
      setRefreshing(true);

      // Load summary
      const summaryResponse = await apiClient.get('/api/v1/analytics/summary') as any;
      setSummary(summaryResponse);

      // Load realtime metrics
      const realtimeResponse = await apiClient.get('/api/v1/analytics/metrics/realtime') as any;
      setRealtimeMetrics(realtimeResponse);

      // Load detailed metrics
      const metricsResponse = await apiClient.get('/api/v1/analytics/metrics', {
        params: {
          metric_names: 'active_users,articles_published,api_requests,errors,page_views',
          time_bucket: 'day',
          days: 30
        }
      }) as any;
      setMetricsData(metricsResponse.metrics);

    } catch (error) {
      console.error('Error loading analytics data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const handleRefresh = () => {
    loadAnalyticsData();
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'down':
        return <TrendingUp className="h-4 w-4 text-red-500 rotate-180" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Cargando analytics...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Analytics</h1>
          <p className="text-gray-600">Métricas y estadísticas de tu plataforma</p>
        </div>
        <Button onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Actualizar
        </Button>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Resumen</TabsTrigger>
          <TabsTrigger value="metrics">Métricas</TabsTrigger>
          <TabsTrigger value="realtime">Tiempo Real</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Usuarios Activos</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.summary.active_users?.total || 0}</div>
                  <div className="flex items-center space-x-2">
                    {getTrendIcon(summary.summary.active_users?.trend || 'stable')}
                    <p className={`text-xs ${getTrendColor(summary.summary.active_users?.trend || 'stable')}`}>
                      {summary.summary.active_users?.trend === 'up' ? 'Aumentando' :
                       summary.summary.active_users?.trend === 'down' ? 'Disminuyendo' : 'Estable'}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Artículos Publicados</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.summary.articles_published?.total || 0}</div>
                  <div className="flex items-center space-x-2">
                    {getTrendIcon(summary.summary.articles_published?.trend || 'stable')}
                    <p className={`text-xs ${getTrendColor(summary.summary.articles_published?.trend || 'stable')}`}>
                      {summary.summary.articles_published?.trend === 'up' ? 'Aumentando' :
                       summary.summary.articles_published?.trend === 'down' ? 'Disminuyendo' : 'Estable'}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Solicitudes API</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.summary.api_requests?.total || 0}</div>
                  <div className="flex items-center space-x-2">
                    {getTrendIcon(summary.summary.api_requests?.trend || 'stable')}
                    <p className={`text-xs ${getTrendColor(summary.summary.api_requests?.trend || 'stable')}`}>
                      {summary.summary.api_requests?.trend === 'up' ? 'Aumentando' :
                       summary.summary.api_requests?.trend === 'down' ? 'Disminuyendo' : 'Estable'}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Errores</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{summary.summary.errors?.total || 0}</div>
                  <div className="flex items-center space-x-2">
                    {getTrendIcon(summary.summary.errors?.trend || 'stable')}
                    <p className={`text-xs ${getTrendColor(summary.summary.errors?.trend || 'stable')}`}>
                      {summary.summary.errors?.trend === 'up' ? 'Aumentando' :
                       summary.summary.errors?.trend === 'down' ? 'Disminuyendo' : 'Estable'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="metrics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {metricsData && Object.entries(metricsData).map(([metricName, dataPoints]) => (
              <Card key={metricName}>
                <CardHeader>
                  <CardTitle className="capitalize">
                    {metricName.replace('_', ' ')}
                  </CardTitle>
                  <CardDescription>
                    Datos históricos de los últimos 30 días
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dataPoints.slice(-7).map((point, index) => (
                      <div key={index} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">
                          {new Date(point.date).toLocaleDateString()}
                        </span>
                        <Badge variant="secondary">{point.value}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="realtime" className="space-y-4">
          {realtimeMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Usuarios Activos (24h)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{realtimeMetrics.active_users_24h}</div>
                  <p className="text-sm text-gray-600">Usuarios únicos en las últimas 24 horas</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Eventos (24h)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{realtimeMetrics.events_last_24h}</div>
                  <p className="text-sm text-gray-600">Total de eventos registrados</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Errores (24h)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-red-600">{realtimeMetrics.errors_last_24h}</div>
                  <p className="text-sm text-gray-600">Errores reportados</p>
                </CardContent>
              </Card>
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Última actualización</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                {realtimeMetrics ? new Date(realtimeMetrics.timestamp).toLocaleString() : 'Nunca'}
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}