"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'

type UserInfo = {
  name: string
  email: string
  roles: string[]
}

export default function Header() {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [mounted, setMounted] = useState(false)

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
  const roleDisplay = primaryRole === 'admin' ? 'Administrador' : 
                      primaryRole === 'gestor' ? 'Gestor' :
                      primaryRole === 'analista' ? 'Analista' : 'Visualizador'

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
              <span className="text-2xl font-bold text-primary-600">ProspecIA</span>
            </Link>
            <span className="text-sm text-gray-400 hidden sm:inline">|</span>
            <span className="text-sm text-secondary-600 hidden sm:inline">
              Sistema de Prospecção e Gestão de Inovação
            </span>
          </div>

          {/* User Info */}
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
    </header>
  )
}
