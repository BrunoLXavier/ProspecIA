'use client'

import Link from 'next/link'
import { useI18n } from '@/lib/hooks/useI18n'

interface AdminFeature {
  titleKey: string
  descriptionKey: string
  href: string
  icon: string
  color: string
}

const ADMIN_FEATURES: AdminFeature[] = [
  {
    titleKey: 'admin.model_config.title',
    descriptionKey: 'admin.model_config.description',
    href: '/admin/model-configs',
    icon: '⚙️',
    color: 'bg-blue-50 border-blue-200',
  },
  {
    titleKey: 'admin.acl.title',
    descriptionKey: 'admin.acl.description',
    href: '/admin/acl',
    icon: '🔐',
    color: 'bg-purple-50 border-purple-200',
  },
  {
    titleKey: 'admin.translations.title',
    descriptionKey: 'admin.translations.description',
    href: '/admin/translations',
    icon: '🌍',
    color: 'bg-green-50 border-green-200',
  },
]

export default function AdminPage() {
  const { t } = useI18n()

  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-primary-600 mb-2">{t('nav.admin')}</h1>
        <p className="text-gray-600">{t('admin.select_feature')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {ADMIN_FEATURES.map((feature) => (
          <Link key={feature.href} href={feature.href}>
            <div className={`border-2 rounded-lg p-6 h-full hover:shadow-lg transition-shadow cursor-pointer ${feature.color}`}>
              <div className="text-4xl mb-3">{feature.icon}</div>
              <h2 className="text-xl font-semibold mb-2 text-gray-900">{t(feature.titleKey)}</h2>
              <p className="text-gray-600 text-sm">{t(feature.descriptionKey)}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
