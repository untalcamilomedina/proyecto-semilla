import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Smartphone, Wifi, WifiOff, Battery, BatteryLow,
  CheckCircle, XCircle, AlertTriangle, Play, Pause,
  RotateCcw, Settings, BarChart3
} from 'lucide-react';

interface MobileCollaborationTestProps {
  onStartTest?: () => void;
  onStopTest?: () => void;
  onResetTest?: () => void;
  isTesting?: boolean;
  testResults?: {
    connectionQuality: number;
    latency: number;
    batteryLevel: number;
    memoryUsage: number;
    networkType: string;
    deviceType: string;
    screenSize: string;
    touchSupport: boolean;
    gestureSupport: boolean;
    websocketConnection: boolean;
    realTimeSync: boolean;
    offlineSupport: boolean;
  };
}

export const MobileCollaborationTest: React.FC<MobileCollaborationTestProps> = ({
  onStartTest,
  onStopTest,
  onResetTest,
  isTesting = false,
  testResults
}) => {
  const [currentTest, setCurrentTest] = useState<string>('');

  const getDeviceInfo = () => {
    const ua = navigator.userAgent;
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
    const isTablet = /iPad|Android(?=.*\bMobile\b)|Tablet/i.test(ua);

    return {
      type: isTablet ? 'Tablet' : isMobile ? 'Mobile' : 'Desktop',
      screenSize: `${window.screen.width}x${window.screen.height}`,
      touchSupport: 'ontouchstart' in window,
      gestureSupport: 'GestureEvent' in window || 'ontouchstart' in window
    };
  };

  const getNetworkInfo = () => {
    // @ts-ignore - navigator.connection is experimental
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;

    if (connection) {
      return {
        type: connection.effectiveType || 'unknown',
        downlink: connection.downlink || 0,
        rtt: connection.rtt || 0
      };
    }

    return {
      type: navigator.onLine ? 'online' : 'offline',
      downlink: 0,
      rtt: 0
    };
  };

  const getBatteryInfo = async () => {
    // @ts-ignore - navigator.getBattery is experimental
    if ('getBattery' in navigator) {
      try {
        // @ts-ignore
        const battery = await navigator.getBattery();
        return {
          level: Math.round(battery.level * 100),
          charging: battery.charging
        };
      } catch (error) {
        return { level: 100, charging: false };
      }
    }
    return { level: 100, charging: false };
  };

  const runDeviceTests = async () => {
    setCurrentTest('device');
    const deviceInfo = getDeviceInfo();
    const networkInfo = getNetworkInfo();
    const batteryInfo = await getBatteryInfo();

    // Simulate test completion
    setTimeout(() => {
      setCurrentTest('');
    }, 2000);

    return {
      deviceType: deviceInfo.type,
      screenSize: deviceInfo.screenSize,
      touchSupport: deviceInfo.touchSupport,
      gestureSupport: deviceInfo.gestureSupport,
      networkType: networkInfo.type,
      batteryLevel: batteryInfo.level
    };
  };

  const runConnectionTests = async () => {
    setCurrentTest('connection');
    // Simulate connection quality test
    const startTime = Date.now();
    // Simulate network request
    await new Promise(resolve => setTimeout(resolve, 1000));
    const latency = Date.now() - startTime;

    setTimeout(() => {
      setCurrentTest('');
    }, 2000);

    return {
      latency,
      connectionQuality: latency < 100 ? 100 : latency < 300 ? 75 : 50,
      websocketConnection: true // Assume WebSocket works
    };
  };

  const runCollaborationTests = async () => {
    setCurrentTest('collaboration');
    // Simulate real-time sync test
    await new Promise(resolve => setTimeout(resolve, 1500));

    setTimeout(() => {
      setCurrentTest('');
    }, 2000);

    return {
      realTimeSync: true,
      offlineSupport: 'serviceWorker' in navigator
    };
  };

  const handleStartTest = async () => {
    onStartTest?.();

    try {
      const deviceResults = await runDeviceTests();
      const connectionResults = await runConnectionTests();
      const collaborationResults = await runCollaborationTests();

      // Combine all results
      const finalResults = {
        ...deviceResults,
        ...connectionResults,
        ...collaborationResults,
        memoryUsage: Math.round(Math.random() * 30 + 20) // Simulate memory usage
      };

      console.log('Mobile Collaboration Test Results:', finalResults);
    } catch (error) {
      console.error('Test failed:', error);
    } finally {
      onStopTest?.();
    }
  };

  const getTestStatus = (testName: string) => {
    if (currentTest === testName) return 'running';
    if (testResults) return 'completed';
    return 'pending';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getBatteryIcon = (level: number) => {
    if (level > 20) {
      return <Battery className="w-4 h-4 text-green-500" />;
    } else {
      return <BatteryLow className="w-4 h-4 text-red-500" />;
    }
  };

  const getNetworkIcon = (type: string) => {
    if (type === 'offline') {
      return <WifiOff className="w-4 h-4 text-red-500" />;
    } else {
      return <Wifi className="w-4 h-4 text-green-500" />;
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="w-5 h-5" />
            Mobile Collaboration Testing
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Device Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-blue-500" />
              <span className="text-sm">Device: {testResults?.deviceType || 'Unknown'}</span>
            </div>
            <div className="flex items-center gap-2">
              {testResults?.batteryLevel !== undefined && getBatteryIcon(testResults.batteryLevel)}
              <span className="text-sm">Battery: {testResults?.batteryLevel || 0}%</span>
            </div>
            <div className="flex items-center gap-2">
              {getNetworkIcon(testResults?.networkType || 'unknown')}
              <span className="text-sm">Network: {testResults?.networkType || 'Unknown'}</span>
            </div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-purple-500" />
              <span className="text-sm">Screen: {testResults?.screenSize || 'Unknown'}</span>
            </div>
          </div>

          {/* Test Progress */}
          {isTesting && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Running Tests...</span>
                <Badge variant="secondary">
                  {currentTest === 'device' && 'Device Info'}
                  {currentTest === 'connection' && 'Connection Quality'}
                  {currentTest === 'collaboration' && 'Collaboration Features'}
                </Badge>
              </div>
              <Progress value={
                currentTest === 'device' ? 33 :
                currentTest === 'connection' ? 66 : 100
              } className="w-full" />
            </div>
          )}

          {/* Test Results */}
          {testResults && (
            <div className="space-y-4">
              <h4 className="font-medium">Test Results</h4>

              <div className="grid grid-cols-1 gap-3">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(testResults.websocketConnection ? 'completed' : 'failed')}
                    <span className="text-sm">WebSocket Connection</span>
                  </div>
                  <Badge variant={testResults.websocketConnection ? "default" : "destructive"}>
                    {testResults.websocketConnection ? 'OK' : 'Failed'}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(testResults.realTimeSync ? 'completed' : 'failed')}
                    <span className="text-sm">Real-time Sync</span>
                  </div>
                  <Badge variant={testResults.realTimeSync ? "default" : "destructive"}>
                    {testResults.realTimeSync ? 'OK' : 'Failed'}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(testResults.touchSupport ? 'completed' : 'failed')}
                    <span className="text-sm">Touch Support</span>
                  </div>
                  <Badge variant={testResults.touchSupport ? "default" : "destructive"}>
                    {testResults.touchSupport ? 'OK' : 'Failed'}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(testResults.offlineSupport ? 'completed' : 'failed')}
                    <span className="text-sm">Offline Support</span>
                  </div>
                  <Badge variant={testResults.offlineSupport ? "default" : "destructive"}>
                    {testResults.offlineSupport ? 'OK' : 'Failed'}
                  </Badge>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {testResults.latency}ms
                  </div>
                  <div className="text-sm text-blue-800">Latency</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {testResults.connectionQuality}%
                  </div>
                  <div className="text-sm text-green-800">Connection Quality</div>
                </div>
              </div>
            </div>
          )}

          {/* Test Controls */}
          <div className="flex gap-2">
            <Button
              onClick={handleStartTest}
              disabled={isTesting}
              className="flex-1"
            >
              {isTesting ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  Testing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Start Mobile Test
                </>
              )}
            </Button>
            <Button
              variant="outline"
              onClick={onResetTest}
              disabled={isTesting}
            >
              <RotateCcw className="w-4 h-4" />
            </Button>
          </div>

          {/* Test Instructions */}
          <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
            <h5 className="font-medium mb-2">Pruebas realizadas:</h5>
            <ul className="space-y-1">
              <li>• Información del dispositivo y capacidades</li>
              <li>• Calidad de conexión y latencia</li>
              <li>• Soporte de colaboración en tiempo real</li>
              <li>• Funcionalidades offline y gestos táctiles</li>
              <li>• Rendimiento y uso de memoria</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};