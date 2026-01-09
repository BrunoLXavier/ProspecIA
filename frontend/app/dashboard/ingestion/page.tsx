'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import IngestionForm from '@/components/features/IngestionForm';
import IngestionTable from '@/components/features/IngestionTable';
import { useI18n } from '@/lib/hooks/useI18n';

export default function IngestionPage() {
  const { t } = useI18n();
  const [refreshKey, setRefreshKey] = useState(0);

  const breadcrumbs = [
    { label: t('dashboard.title'), href: '/dashboard' },
    { label: t('ingestion.title') },
  ];

  const handleFormSubmit = () => {
    // Refresh table after form submission
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb Navigation */}
        <nav className="flex mb-4" aria-label="Breadcrumb">
          <ol className="inline-flex items-center space-x-1 md:space-x-3">
            {breadcrumbs.map((breadcrumb, index) => (
              <li key={index} className="inline-flex items-center">
                {index > 0 && (
                  <svg
                    className="w-3 h-3 text-gray-400 mx-1"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
                {breadcrumb.href ? (
                  <a
                    href={breadcrumb.href}
                    className="text-sm font-medium text-gray-700 hover:text-blue-600"
                  >
                    {breadcrumb.label}
                  </a>
                ) : (
                  <span className="text-sm font-medium text-gray-500">
                    {breadcrumb.label}
                  </span>
                )}
              </li>
            ))}
          </ol>
        </nav>

        {/* Page Title and Description */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {t('ingestion.title')}
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            {t('ingestion.description')}
          </p>
        </div>

        {/* Form Section */}
        <div className="bg-white shadow sm:rounded-lg mb-8 p-6">
          <IngestionForm onSubmit={handleFormSubmit} />
        </div>

        {/* Table Section */}
        <div className="bg-white shadow sm:rounded-lg">
          <IngestionTable key={refreshKey} />
        </div>

        {/* Back Button */}
        <div className="flex justify-start mt-8">
          <a
            href="/dashboard"
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            {t('common.back')}
          </a>
        </div>
      </div>
    </DashboardLayout>
  );
}
