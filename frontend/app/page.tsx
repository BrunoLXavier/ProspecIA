'use client'

import Link from 'next/link'
import { useI18n } from '@/lib/hooks/useI18n'

export default function HomePage() {
  const { t } = useI18n()
  
  const docsUrl = process.env.NEXT_PUBLIC_API_URL
    ? `${process.env.NEXT_PUBLIC_API_URL}/docs`
    : 'http://localhost:8000/docs'

  return (
    <main className="flex min-h-screen flex-col items-center justify-start pt-6 sm:pt-12 lg:pt-24 px-6 sm:px-12 lg:px-24 pb-24">
      <div className="relative flex place-items-center mt-8">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-secondary-900 mb-4">
            {t('home.title')}
          </h2>
          <p className="text-secondary-600 mb-8 max-w-2xl mx-auto text-center">
            {t('home.description')}
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link href="/dashboard" className="btn-primary">
              {t('home.access_dashboard')}
            </Link>
            <Link href="/admin" className="btn-secondary">
              {t('home.admin_panel')}
            </Link>
            <a href={docsUrl} className="btn-secondary" target="_blank" rel="noreferrer">
              {t('home.documentation')}
            </a>
          </div>
          
          <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl">
            <div className="card text-left">
              <h3 className="text-lg font-semibold text-primary-600 mb-2">
                🎯 {t('home.feature.complete_management.title')}
              </h3>
              <p className="text-sm text-secondary-600">
                {t('home.feature.complete_management.description')}
              </p>
            </div>
            
            <div className="card text-left">
              <h3 className="text-lg font-semibold text-primary-600 mb-2">
                🤖 {t('home.feature.responsible_ai.title')}
              </h3>
              <p className="text-sm text-secondary-600">
                {t('home.feature.responsible_ai.description')}
              </p>
            </div>
            
            <div className="card text-left">
              <h3 className="text-lg font-semibold text-primary-600 mb-2">
                🔒 {t('home.feature.lgpd_compliance.title')}
              </h3>
              <p className="text-sm text-secondary-600">
                {t('home.feature.lgpd_compliance.description')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
