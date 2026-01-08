'use client'

import { useEffect } from 'react'
import { useI18n } from '@/lib/hooks/useI18n'

/**
 * Client component to dynamically update HTML lang attribute based on current locale
 */
export function DynamicHtmlLang() {
  const { locale } = useI18n()

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.lang = locale
    }
  }, [locale])

  return null
}
