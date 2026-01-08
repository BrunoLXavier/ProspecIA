"use client"

import { useEffect, useState } from 'react'
import { useI18n } from '@/lib/hooks/useI18n'

type FieldConfig = {
  id: string
  model_name: string
  field_name: string
  field_type: string
  label_key?: string
  validators?: Record<string, any>
  visibility_rule?: string
  required?: boolean
  default_value?: any
  description?: string
  created_at?: string
  updated_at?: string
  created_by?: string
}

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ModelConfigsPage() {
  const { t } = useI18n()
  const [model, setModel] = useState<string>('Ingestao')
  const [items, setItems] = useState<FieldConfig[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<Record<string, Partial<FieldConfig>>>({})

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API}/system/model-configs/${encodeURIComponent(model)}`)
      if (!res.ok) throw new Error(`Failed to load: ${res.status}`)
      const data: FieldConfig[] = await res.json()
      setItems(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [model])

  async function saveRow(row: FieldConfig) {
    const patch = editing[row.field_name]
    if (!patch) return
    try {
      const res = await fetch(`${API}/system/model-configs/${encodeURIComponent(model)}/${encodeURIComponent(row.field_name)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          label_key: patch.label_key ?? row.label_key,
          visibility_rule: patch.visibility_rule ?? row.visibility_rule,
          required: patch.required ?? row.required,
          description: patch.description ?? row.description,
        })
      })
      if (!res.ok) throw new Error(`Failed to save: ${res.status}`)
      const updated: FieldConfig = await res.json()
      setItems(prev => prev.map(it => it.field_name === updated.field_name ? updated : it))
      setEditing(prev => { const n = { ...prev }; delete n[row.field_name]; return n })
    } catch (e: any) {
      alert(e.message)
    }
  }

  function setEdit(field: string, patch: Partial<FieldConfig>) {
    setEditing(prev => ({ ...prev, [field]: { ...prev[field], ...patch } }))
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">{t('config.title')}</h1>
      <p className="text-secondary-600 mb-6">{t('config.description')}</p>

      <div className="flex items-center gap-3 mb-4">
        <label className="text-sm text-secondary-700">{t('config.model')}</label>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="border rounded-md px-2 py-1"
        >
          <option>Ingestao</option>
          <option>Consentimento</option>
        </select>
        <button
          className="ml-auto border rounded-md px-3 py-1 text-sm hover:bg-gray-50"
          onClick={load}
        >{t('button.refresh', 'Atualizar')}</button>
      </div>

      {loading && <div>{t('message.loading')}</div>}
      {error && <div className="text-red-600">{error}</div>}

      {!loading && !error && (
        <div className="overflow-x-auto border rounded-md">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 text-left">
              <tr>
                <th className="px-3 py-2">{t('config.field')}</th>
                <th className="px-3 py-2">{t('config.field_type')}</th>
                <th className="px-3 py-2">{t('config.label')}</th>
                <th className="px-3 py-2">{t('config.visibility')}</th>
                <th className="px-3 py-2">{t('config.required')}</th>
                <th className="px-3 py-2 w-40">{t('form.description')}</th>
                <th className="px-3 py-2"></th>
              </tr>
            </thead>
            <tbody>
              {items.map(row => {
                const edit = editing[row.field_name] || {}
                return (
                  <tr key={row.id} className="border-t">
                    <td className="px-3 py-2 font-medium">{row.field_name}</td>
                    <td className="px-3 py-2 text-secondary-700">{row.field_type}</td>
                    <td className="px-3 py-2">
                      <input
                        className="border rounded px-2 py-1 w-56"
                        defaultValue={row.label_key || ''}
                        onChange={(e) => setEdit(row.field_name, { label_key: e.target.value })}
                      />
                    </td>
                    <td className="px-3 py-2">
                      <select
                        className="border rounded px-2 py-1"
                        defaultValue={row.visibility_rule || 'all'}
                        onChange={(e) => setEdit(row.field_name, { visibility_rule: e.target.value })}
                      >
                        <option value="all">{t('config.visibility_all')}</option>
                        <option value="admin">{t('config.visibility_admin')}</option>
                        <option value="non_viewer">{t('config.visibility_non_viewer')}</option>
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <input
                        type="checkbox"
                        defaultChecked={!!row.required}
                        onChange={(e) => setEdit(row.field_name, { required: e.target.checked })}
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        className="border rounded px-2 py-1 w-40"
                        defaultValue={row.description || ''}
                        onChange={(e) => setEdit(row.field_name, { description: e.target.value })}
                      />
                    </td>
                    <td className="px-3 py-2 text-right">
                      <button
                        className="border rounded px-3 py-1 text-sm hover:bg-gray-50"
                        onClick={() => saveRow(row)}
                      >{t('button.save')}</button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
