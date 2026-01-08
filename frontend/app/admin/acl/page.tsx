"use client"

import { useEffect, useState } from 'react'
import { useI18n } from '@/lib/hooks/useI18n'

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

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">{t('acl.title')}</h1>
      <p className="text-secondary-600 mb-6">{t('acl.description')}</p>

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
          <button className="border rounded px-3 py-1 text-sm hover:bg-gray-50" onClick={createRule}>{t('acl.create_rule')}</button>
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
                    <button className="border rounded px-3 py-1 text-sm hover:bg-gray-50" onClick={() => deleteRule(r.id)}>{t('acl.delete_rule')}</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
