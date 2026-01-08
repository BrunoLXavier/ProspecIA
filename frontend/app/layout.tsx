import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

// Static metadata for SEO
// Note: Title and description are in pt-BR as default
// Client-side translations are handled by next-i18next
export const metadata: Metadata = {
  title: 'ProspecIA - Gestão de Inovação',
  description: 'Sistema de Prospecção e Gestão de Inovação com IA Responsável',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
  themeColor: '#0ea5e9',
  icons: {
    icon: '/favicon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Note: lang attribute is dynamically managed by client-side i18n
  // Default to pt-BR, but will be updated by useI18n hook
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className="bg-secondary-50 font-sans antialiased">
        <Header />
        <Providers>{children}</Providers>
        <Footer />
      </body>
    </html>
  )
}
