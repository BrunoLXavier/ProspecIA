/**
 * Portfolio page
 */

'use client';
import DashboardSidebar from '@/components/layout/DashboardSidebar';
import { useI18n } from '@/lib/hooks/useI18n';

export default function PortfolioPage() {
  const { t } = useI18n();
  return (
    <div className="flex min-h-screen bg-gray-100">
      <DashboardSidebar />
      <main className="flex-1 flex flex-col items-center justify-start pt-6 sm:pt-12 lg:pt-24 px-6 sm:px-12 lg:px-24 pb-24">
        <div className="w-full max-w-5xl">
          <h1 className="text-4xl font-bold text-primary-600 mb-4">{t('portfolio.title')}</h1>
          <p className="text-secondary-600 mb-6">{t('portfolio.description')}</p>
          {/* Conteúdo da página Portfolio */}
        </div>
      </main>
    </div>
  );
}
