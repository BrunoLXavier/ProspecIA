'use client';

import { useI18n } from '@/lib/hooks/useI18n';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';

export default function OpportunitiesPage() {
  const { t } = useI18n();

  const breadcrumbs = [
    { label: t('dashboard.title'), href: '/dashboard' },
    { label: t('opportunities.title') },
  ];

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <nav className="flex mb-4" aria-label="Breadcrumb">
          <ol className="inline-flex items-center space-x-1 md:space-x-3">
            {breadcrumbs.map((breadcrumb, index) => (
              <li key={index} className="inline-flex items-center">
                {index > 0 && (
                  <svg className="w-3 h-3 text-gray-400 mx-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {breadcrumb.href ? (
                  <a href={breadcrumb.href} className="text-sm font-medium text-gray-700 hover:text-blue-600">{breadcrumb.label}</a>
                ) : (
                  <span className="text-sm font-medium text-gray-500">{breadcrumb.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{t('opportunities.title')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('opportunities.description')}</p>
        </div>

        <div className="bg-white shadow sm:rounded-lg p-8">
          <p className="text-center text-gray-500">Opportunities management page - Ready for StandardPageLayout implementation</p>
        </div>

        <div className="flex justify-start mt-8">
          <a href="/dashboard" className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            {t('common.back')}
          </a>
        </div>
      </div>
    </DashboardLayout>
  );
}
