'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useI18n } from '@/lib/hooks/useI18n'

interface AdminMenuItem {
  href: string
  labelKey: string
  icon: string
}

const ADMIN_MENU: AdminMenuItem[] = [
  { href: '/admin/model-configs', labelKey: 'admin.model_config.title', icon: '⚙️' },
  { href: '/admin/acl', labelKey: 'admin.acl.title', icon: '🔐' },
  { href: '/admin/translations', labelKey: 'admin.translations.title', icon: '🌍' },
]

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { t } = useI18n()

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg">
        <nav className="p-6">
          <h2 className="text-xl font-bold mb-6 text-primary-600">{t('nav.admin')}</h2>
          <ul className="space-y-2">
            {ADMIN_MENU.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center space-x-3 px-4 py-2 rounded-lg transition-colors ${
                    pathname === item.href
                      ? 'bg-primary-100 text-primary-700 font-semibold'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
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
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}
