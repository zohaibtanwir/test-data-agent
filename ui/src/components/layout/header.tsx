'use client';

import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { MacysLogo } from '@/components/ui/macys-logo';
import { api } from '@/lib/api-client';

export function Header() {
  const [status, setStatus] = useState<'healthy' | 'degraded' | 'unhealthy'>('unhealthy');
  const [isChecking, setIsChecking] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      setIsChecking(true);
      try {
        const response = await api.health.check();
        setStatus(response.status);
      } catch (error) {
        setStatus('unhealthy');
      } finally {
        setIsChecking(false);
      }
    };

    // Initial check
    checkHealth();

    // Check health every 30 seconds
    const interval = setInterval(checkHealth, 30000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500';
      case 'degraded':
        return 'bg-yellow-500';
      default:
        return 'bg-red-500';
    }
  };

  return (
    <header className="fixed top-0 w-full h-16 bg-white border-b border-border-default shadow-sm z-50">
      <div className="flex items-center justify-between h-full px-6">
        <div className="flex items-center space-x-4">
          <MacysLogo className="h-8 w-auto" />
          <div className="flex items-center space-x-3 border-l border-gray-300 pl-4 ml-2">
            <span className="text-lg font-semibold text-gray-700">
              Test Data Agent
            </span>
            <Badge variant="outline" className="border-border-default">
              <span className={`inline-block w-2 h-2 mr-2 rounded-full ${getStatusColor()} ${isChecking ? 'animate-pulse' : ''}`} />
              Service {status}
            </Badge>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <span className="text-sm text-macys-gray">
            AI-Powered Test Data Generation
          </span>
        </div>
      </div>
    </header>
  );
}