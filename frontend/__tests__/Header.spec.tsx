import { render, screen } from '@testing-library/react'
import React from 'react'

vi.mock('next/link', () => ({
  default: ({ href, children }: any) => <a href={href}>{children}</a>,
}))

vi.mock('@/lib/hooks/useI18n', () => ({
  useI18n: () => ({
    locale: 'pt-BR',
    t: (key: string) => ({ 'app.title': 'ProspecIA', 'app.subtitle': 'Sistema de Prospecção e Gestão de Inovação' } as any)[key] || key,
    changeLanguage: async () => {},
    isLoading: false,
    availableLocales: ['pt-BR', 'en-US'],
  }),
}))

import Header from '@/components/layout/Header'

describe('Header', () => {
  it('renders title and subtitle from i18n', () => {
    render(<Header />)
    expect(screen.getByText('ProspecIA')).toBeInTheDocument()
    expect(screen.getByText('Sistema de Prospecção e Gestão de Inovação')).toBeInTheDocument()
  })
})
