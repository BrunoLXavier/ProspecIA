"use client"

import { useEffect, useState } from 'react'
import { useI18n } from '@/lib/hooks/useI18n'
import Link from 'next/link'

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

  const breadcrumbs = [
    { label: t('nav.admin'), href: '/admin' },
    { label: t('admin.model_config.title') },
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
          <h1 className="text-3xl font-bold text-gray-900">{t('admin.model_config.title')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('admin.model_config.description')}</p>
        </div>

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
          className="ml-auto bg-primary-600 text-white rounded px-4 py-2 text-sm font-semibold shadow hover:bg-primary-700 transition"
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
                        className="bg-primary-600 text-white rounded px-4 py-2 text-sm font-semibold shadow hover:bg-primary-700 transition"
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
