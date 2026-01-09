'use client'

import { useEffect, useState } from 'react'
import { useI18n } from '@/lib/hooks/useI18n'
import { get, post, patch, del } from '@/lib/api/client'
import toast from 'react-hot-toast'
import Link from 'next/link'

type TranslationKey = {
  id: string
  key: string
  namespace: string
  pt_br: string
  en_us: string
  es_es: string
  created_at: string
  updated_at: string
  created_by: string
  updated_by: string
}

const NAMESPACES = ['common', 'ingestion', 'wave2']
const LANGUAGES = [
  { code: 'pt_br', label: 'pt-BR' },
  { code: 'en_us', label: 'en-US' },
  { code: 'es_es', label: 'es-ES' },
]

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function TranslationsAdminPage() {
  const { t } = useI18n()
  const [keys, setKeys] = useState<TranslationKey[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterNamespace, setFilterNamespace] = useState('common')
  const [filterLanguage, setFilterLanguage] = useState('')
  
  const [showModal, setShowModal] = useState(false)
  const [editingKey, setEditingKey] = useState<TranslationKey | null>(null)
  const [formData, setFormData] = useState({
    key: '',
    namespace: 'common',
    pt_br: '',
    en_us: '',
    es_es: '',
  })

  const loadKeys = async () => {
    setLoading(true)
    try {
      const res = await get<TranslationKey[]>(`${API}/system/translations`)
      setKeys(res)
    } catch (e: any) {
      toast.error(t('admin:message.error'))
      console.error('Failed to load translations:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadKeys()
  }, [])

  const filteredKeys = keys.filter(item => {
    const matchesSearch = 
      item.key.toLowerCase().includes(search.toLowerCase()) ||
      item.pt_br.toLowerCase().includes(search.toLowerCase()) ||
      item.en_us.toLowerCase().includes(search.toLowerCase()) ||
      item.es_es.toLowerCase().includes(search.toLowerCase())
    
    const matchesNamespace = filterNamespace === '' || item.namespace === filterNamespace
    
    return matchesSearch && matchesNamespace
  })

  const handleOpenModal = (key?: TranslationKey) => {
    if (key) {
      setEditingKey(key)
      setFormData({
        key: key.key,
        namespace: key.namespace,
        pt_br: key.pt_br,
        en_us: key.en_us,
        es_es: key.es_es,
      })
    } else {
      setEditingKey(null)
      setFormData({
        key: '',
        namespace: 'common',
        pt_br: '',
        en_us: '',
        es_es: '',
      })
    }
    setShowModal(true)
  }

  const handleSave = async () => {
    if (!formData.key || !formData.pt_br || !formData.en_us || !formData.es_es) {
      toast.error(t('admin:form.required'))
      return
    }

    try {
      if (editingKey) {
        await patch(
          `${API}/system/translations/${editingKey.id}`,
          formData
        )
        toast.success(t('admin:message.success_update'))
      } else {
        await post(`${API}/system/translations`, formData)
        toast.success(t('admin:message.success_create'))
      }
      setShowModal(false)
      await loadKeys()
    } catch (e: any) {
      toast.error(t('admin:message.error'))
      console.error('Error saving translation:', e)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm(t('admin:modal.confirm_delete'))) return
    
    try {
      await del(`${API}/system/translations/${id}`)
      toast.success(t('admin:message.success_delete'))
      await loadKeys()
    } catch (e: any) {
      toast.error(t('admin:message.error'))
      console.error('Error deleting translation:', e)
    }
  }

  const handleExport = () => {
    const dataStr = JSON.stringify(keys, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `translations_${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    toast.success(t('admin:export.success'))
  }

  const breadcrumbs = [
    { label: t('nav.admin'), href: '/admin' },
    { label: t('admin.translations.title') },
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
          <h1 className="text-3xl font-bold text-gray-900">{t('admin.translations.title')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('admin.translations.description')}</p>
        </div>

      {/* Toolbar */}
      <div className="bg-white rounded-lg shadow mb-6 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <input
              type="text"
              placeholder={t('admin:table.search_placeholder')}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <select
              value={filterNamespace}
              onChange={(e) => setFilterNamespace(e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">{t('admin:filter.all_namespaces')}</option>
              {NAMESPACES.map(ns => (
                <option key={ns} value={ns}>{t(`admin:namespace.${ns}`)}</option>
              ))}
            </select>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => handleOpenModal()}
              className="flex-1 bg-primary-600 text-white rounded px-4 py-2 font-semibold shadow hover:bg-primary-700 transition"
            >
              {t('admin:button.add_key')}
            </button>
            <button
              onClick={handleExport}
              className="flex-1 bg-green-600 text-white rounded px-4 py-2 font-semibold shadow hover:bg-green-700 transition"
            >
              {t('admin:button.export')}
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <div className="text-center py-8">{t('admin:message.loading')}</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">{t('admin:table.key')}</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">{t('admin:table.namespace')}</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">{t('admin:table.pt_br')}</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">{t('admin:table.en_us')}</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">{t('admin:table.es_es')}</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">{t('admin:table.actions')}</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredKeys.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    {t('admin:table.no_data')}
                  </td>
                </tr>
              ) : (
                filteredKeys.map(item => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-3 font-mono text-sm">{item.key}</td>
                    <td className="px-6 py-3 text-sm">
                      <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                        {item.namespace}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm max-w-xs truncate">{item.pt_br}</td>
                    <td className="px-6 py-3 text-sm max-w-xs truncate">{item.en_us}</td>
                    <td className="px-6 py-3 text-sm max-w-xs truncate">{item.es_es}</td>
                    <td className="px-6 py-3 text-sm">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleOpenModal(item)}
                          className="text-primary-600 font-semibold hover:underline"
                        >
                          {t('admin:button.edit')}
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="text-red-600 font-semibold hover:underline"
                        >
                          {t('admin:button.delete')}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-96 overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingKey ? t('admin:modal.edit_title') : t('admin:modal.add_title')}
            </h2>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">{t('admin:form.key_label')}</label>
                  <input
                    type="text"
                    value={formData.key}
                    onChange={(e) => setFormData({ ...formData, key: e.target.value })}
                    placeholder={t('admin:form.key_placeholder')}
                    disabled={!!editingKey}
                    className="w-full border rounded px-3 py-2 disabled:bg-gray-100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">{t('admin:form.namespace_label')}</label>
                  <select
                    value={formData.namespace}
                    onChange={(e) => setFormData({ ...formData, namespace: e.target.value })}
                    className="w-full border rounded px-3 py-2"
                  >
                    {NAMESPACES.map(ns => (
                      <option key={ns} value={ns}>{ns}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">{t('admin:form.pt_br_label')}</label>
                <textarea
                  value={formData.pt_br}
                  onChange={(e) => setFormData({ ...formData, pt_br: e.target.value })}
                  className="w-full border rounded px-3 py-2 min-h-24"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">{t('admin:form.en_us_label')}</label>
                <textarea
                  value={formData.en_us}
                  onChange={(e) => setFormData({ ...formData, en_us: e.target.value })}
                  className="w-full border rounded px-3 py-2 min-h-24"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">{t('admin:form.es_es_label')}</label>
                <textarea
                  value={formData.es_es}
                  onChange={(e) => setFormData({ ...formData, es_es: e.target.value })}
                  className="w-full border rounded px-3 py-2 min-h-24"
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSave}
                className="flex-1 bg-primary-600 text-white rounded px-4 py-2 font-semibold shadow hover:bg-primary-700 transition"
              >
                {t('admin:button.save')}
              </button>
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 border rounded px-4 py-2 font-semibold shadow hover:bg-gray-50 transition"
              >
                {t('admin:button.cancel')}
              </button>
            </div>
          </div>
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
