/**
 * Pipeline page (root path)
 */

'use client';

import { OpportunitiesPipeline } from '@/components/features/OpportunitiesPipeline';
import Link from 'next/link';
import { useI18n } from '@/lib/hooks/useI18n';
import DashboardSidebar from '@/components/layout/DashboardSidebar';

export default function PipelinePage() {
  const { t } = useI18n();
  return (
    <div className="flex min-h-screen bg-gray-100">
      <DashboardSidebar />
      <main className="flex-1 flex flex-col items-center justify-start pt-6 sm:pt-12 lg:pt-24 px-6 sm:px-12 lg:px-24 pb-24">
        <div className="w-full max-w-5xl">
          <h1 className="text-4xl font-bold text-primary-600 mb-4">{t('opportunities.title')}</h1>
          <OpportunitiesPipeline />
          <div className="mt-8">
            <Link href="/" className="btn-primary">← {t('dashboard.back_home')}</Link>
          </div>
        </div>
      </main>
    </div>
  );
}
