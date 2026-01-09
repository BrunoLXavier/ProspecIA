'use client'

import IngestaoForm from '@/components/features/IngestaoForm'
import IngestaoTable from '@/components/features/IngestaoTable'
import { useI18n } from '@/lib/hooks/useI18n'
import Link from 'next/link'

function DashboardBreadcrumb() {
  return (
    <nav className="flex mb-6" aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-3">
        <li className="inline-flex items-center">
          <Link href="/dashboard" className="text-primary-600 hover:underline font-medium">Dashboard</Link>
        </li>
      </ol>
    </nav>
  );
}

const DASHBOARD_MENU = [
  { href: '/dashboard', labelKey: 'dashboard.title', icon: '🏠' },
  { href: '/funding-sources', labelKey: 'funding_sources.title', icon: '💰' },
  { href: '/clients', labelKey: 'clients.title', icon: '👤' },
  { href: '/interactions', labelKey: 'interactions.title', icon: '💬' },
  { href: '/portfolio', labelKey: 'portfolio.title', icon: '📁' },
  { href: '/pipeline', labelKey: 'opportunities.title', icon: '🚀' }
];

export default function DashboardPage() {
  const { t } = useI18n();
  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg">
        <nav className="p-6">
          <h2 className="text-xl font-bold mb-6 text-primary-600">{t('dashboard.menu_title')}</h2>
          <ul className="space-y-2">
            {DASHBOARD_MENU.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors text-gray-700 hover:bg-gray-100`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span>{t(item.labelKey)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>
      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center justify-start pt-6 sm:pt-12 lg:pt-24 px-6 sm:px-12 lg:px-24 pb-24">
        <div className="w-full max-w-5xl">
          <DashboardBreadcrumb />
          <h1 className="text-4xl font-bold text-primary-600 mb-4">{t('dashboard.title')}</h1>
          <p className="text-secondary-600 mb-6">{t('dashboard.description')}</p>
          {/* Components */}
          {/** @ts-ignore **/}
          <IngestaoForm />
          {/** @ts-ignore **/}
          <IngestaoTable />
          <div className="mt-8">
            <Link href="/" className="btn-primary">← {t('dashboard.back_home')}</Link>
          </div>
        </div>
      </main>
    </div>
  );
}
