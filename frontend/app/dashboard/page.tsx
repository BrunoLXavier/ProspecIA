'use client'

import { useI18n } from '@/lib/hooks/useI18n'
import { DashboardGrid } from '@/components/dashboard/DashboardGrid'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import Breadcrumb from '@/components/Breadcrumb';

export default function DashboardPage() {
  const { t } = useI18n();
  
  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Breadcrumb
          items={[
            { label: t('dashboard.title'), href: '/dashboard' }
          ]}
        />
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {t('dashboard.title')}
          </h1>
          <p className="text-lg text-gray-600">
            {t('dashboard.description')}
          </p>
        </div>

        {/* Dashboard Grid */}
        <DashboardGrid />
      </div>
    </DashboardLayout>
  );
}
