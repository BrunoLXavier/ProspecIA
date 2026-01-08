"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useI18n } from '@/lib/hooks/useI18n'

type UserInfo = {
  name: string
  email: string
  roles: string[]
}

export default function Header() {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [mounted, setMounted] = useState(false)
  const { locale, changeLanguage, availableLocales, t } = useI18n()

  useEffect(() => {
    setMounted(true)
    // Simulate getting user info from auth context or API
    // In production, this would come from NextAuth or similar
    const mockUser: UserInfo = {
      name: "Admin User",
      email: "admin@prospecai.com.br",
      roles: ["admin", "gestor"]
    }
    setUser(mockUser)
  }, [])

  if (!mounted) {
    return null
  }

  const primaryRole = user?.roles[0] || 'viewer'
  const roleDisplay = t(`role.${primaryRole}`)

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <span className="text-2xl font-bold text-primary-600">{t('app.title')}</span>
            </Link>
            <span className="text-sm text-gray-400 hidden sm:inline">|</span>
            <span className="text-sm text-secondary-600 hidden sm:inline">
              {t('app.subtitle')}
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <nav className="hidden md:flex items-center space-x-6">
              <Link href="/" className="text-sm text-secondary-700 hover:text-primary-600 transition-colors">
                {t('nav.home')}
              </Link>
              <Link href="/dashboard" className="text-sm text-secondary-700 hover:text-primary-600 transition-colors">
                {t('nav.dashboard')}
              </Link>
              <Link href="/admin" className="text-sm text-secondary-700 hover:text-primary-600 transition-colors">
                {t('nav.admin')}
              </Link>
            </nav>
            
            <div className="flex items-center space-x-2">
              <label htmlFor="language" className="text-sm text-secondary-600">{t('header.language')}</label>
              <select
                id="language"
                value={locale}
                onChange={(e) => changeLanguage(e.target.value)}
                className="text-sm border border-gray-300 rounded-md px-2 py-1 bg-white text-secondary-700"
              >
                {availableLocales.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>

            {user && (
              <div className="flex items-center space-x-4">
                <div className="text-right hidden md:block">
                  <p className="text-sm font-medium text-secondary-900">{user.name}</p>
                  <p className="text-xs text-secondary-500">{roleDisplay}</p>
                </div>
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary-600 text-white font-semibold">
                  {user.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
