"use client"

import { useState, useEffect } from 'react'
import { useI18n } from '@/lib/hooks/useI18n'

interface SystemInfo {
  application: {
    name: string
    version: string
    environment: string
    debug: boolean
  }
  environment: Record<string, any>
  features: Record<string, boolean>
  timestamp: string
}

export default function Footer() {
  const { t } = useI18n();
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [wave, setWave] = useState<string>(t('footer.wave_default'));
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setWave(process.env.NEXT_PUBLIC_WAVE || 'Onda 1');
    const fetchSystemInfo = async () => {
      try {
        const response = await fetch('http://localhost:8000/system/info', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (response.ok) {
          const data: SystemInfo = await response.json();
          setSystemInfo(data);
        }
      } catch (error) {
        console.error('Error fetching system info:', error);
      }
    };
    fetchSystemInfo();
  }, []);

  if (!mounted) {
    return null;
  }

  const lastUpdate = systemInfo
    ? new Date(systemInfo.timestamp).toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      })
    : new Date().toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      });

  const version = systemInfo?.application.version || '1.0.0';

  return (
    <footer className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 shadow-lg">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="py-3 flex justify-between items-center text-sm text-gray-600">
          <div className="flex items-center space-x-6">
            <span>
              <strong>{t('footer.wave')}:</strong> {wave}
            </span>
            <span>
              <strong>{t('footer.version')}:</strong> {version}
            </span>
          </div>
          <span>
            <strong>{t('footer.last_update')}:</strong> {lastUpdate}
          </span>
        </div>
      </div>
    </footer>
  );
}
