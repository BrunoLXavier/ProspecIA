'use client';

import { useI18n } from '@/lib/hooks/useI18n';
import { AdminGrid } from '@/components/admin/AdminGrid';
import Breadcrumb from '@/components/Breadcrumb';

export default function AdminPage() {
  const { t } = useI18n();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Breadcrumb
          items={[
            { label: t('nav.admin'), href: '/admin' }
          ]}
        />
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {t('nav.admin')}
          </h1>
          <p className="text-lg text-gray-600">
            {t('admin.select_feature')}
          </p>
        </div>

        {/* Admin Grid */}
        <AdminGrid />
      </div>
  );
}
