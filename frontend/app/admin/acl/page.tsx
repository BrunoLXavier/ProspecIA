"use client"

import { useEffect, useState } from 'react'
import { useI18n } from '@/lib/hooks/useI18n'
import Link from 'next/link'

type ACLRule = {
  id: string
  role: string
  resource: string
  action: string
  condition?: string
  description?: string
}

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ACLPage() {
  const { t } = useI18n()
  const [items, setItems] = useState<ACLRule[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState<Partial<ACLRule>>({ role: 'admin', resource: 'system', action: 'read' })

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/system/acl/rules`)
      if (!res.ok) throw new Error(`Failed to load: ${res.status}`)
      const data: ACLRule[] = await res.json()
      setItems(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function createRule() {
    try {
      const res = await fetch(`${API}/system/acl/rules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      if (!res.ok) throw new Error(`Failed to create: ${res.status}`)
      await load()
      setForm({ role: 'admin', resource: 'system', action: 'read' })
    } catch (e: any) {
      alert(e.message)
    }
  }

  async function deleteRule(id: string) {
    if (!confirm(t('message.confirm_delete'))) return
    try {
      const res = await fetch(`${API}/system/acl/rules/${encodeURIComponent(id)}`, { method: 'DELETE' })
      if (!res.ok) throw new Error(`Failed to delete: ${res.status}`)
      setItems(prev => prev.filter(r => r.id !== id))
    } catch (e: any) {
      alert(e.message)
    }
  }

  const breadcrumbs = [
    { label: t('nav.admin'), href: '/admin' },
    { label: t('admin.acl.title') },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Breadcrumb */}
        <nav className="flex mb-4" aria-label="Breadcrumb">
          <ol className="inline-flex items-center space-x-1 md:space-x-3">
            {breadcrumbs.map((breadcrumb, index) => (
              <li key={index} className="inline-flex items-center">
                {index > 0 && (
                  <svg className="w-3 h-3 text-gray-400 mx-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {breadcrumb.href ? (
                  <a href={breadcrumb.href} className="text-sm font-medium text-gray-700 hover:text-blue-600">
                    {breadcrumb.label}
                  </a>
                ) : (
                  <span className="text-sm font-medium text-gray-500">{breadcrumb.label}</span>
                )}
              </li>
            ))}
          </ol>
        </nav>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{t('admin.acl.title')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('admin.acl.description')}</p>
        </div>

      <div className="border rounded-md p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div>
            <label className="text-sm text-secondary-700">{t('acl.role')}</label>
            <input className="border rounded px-2 py-1 w-full" value={form.role || ''} onChange={e => setForm({ ...form, role: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-secondary-700">{t('acl.resource')}</label>
            <input className="border rounded px-2 py-1 w-full" value={form.resource || ''} onChange={e => setForm({ ...form, resource: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-secondary-700">{t('acl.action')}</label>
            <input className="border rounded px-2 py-1 w-full" value={form.action || ''} onChange={e => setForm({ ...form, action: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-secondary-700">{t('acl.condition')}</label>
            <input className="border rounded px-2 py-1 w-full" value={form.condition || ''} onChange={e => setForm({ ...form, condition: e.target.value })} />
          </div>
          <div>
            <label className="text-sm text-secondary-700">{t('acl.description_field')}</label>
            <input className="border rounded px-2 py-1 w-full" value={form.description || ''} onChange={e => setForm({ ...form, description: e.target.value })} />
          </div>
        </div>
        <div className="mt-3 text-right">
          <button className="bg-primary-600 text-white rounded px-4 py-2 text-sm font-semibold shadow hover:bg-primary-700 transition" onClick={createRule}>{t('acl.create_rule')}</button>
        </div>
      </div>

      {loading && <div>{t('message.loading')}</div>}
      {error && <div className="text-red-600">{error}</div>}

      {!loading && !error && (
        <div className="overflow-x-auto border rounded-md">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-left">
              <tr>
                <th className="px-3 py-2">{t('acl.role')}</th>
                <th className="px-3 py-2">{t('acl.resource')}</th>
                <th className="px-3 py-2">{t('acl.action')}</th>
                <th className="px-3 py-2">{t('acl.condition')}</th>
                <th className="px-3 py-2">{t('acl.description_field')}</th>
                <th className="px-3 py-2 w-20"></th>
              </tr>
            </thead>
            <tbody>
              {items.map(r => (
                <tr key={r.id} className="border-t">
                  <td className="px-3 py-2">{r.role}</td>
                  <td className="px-3 py-2">{r.resource}</td>
                  <td className="px-3 py-2">{r.action}</td>
                  <td className="px-3 py-2">{r.condition || '-'}</td>
                  <td className="px-3 py-2">{r.description || '-'}</td>
                  <td className="px-3 py-2 text-right">
                    <button className="bg-red-600 text-white rounded px-4 py-2 text-sm font-semibold shadow hover:bg-red-700 transition" onClick={() => deleteRule(r.id)}>{t('acl.delete_rule')}</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Back Button */}
      <div className="flex justify-start mt-8">
        <a
          href="/admin"
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          {t('common.back')}
        </a>
      </div>
    </div>
  )
}
