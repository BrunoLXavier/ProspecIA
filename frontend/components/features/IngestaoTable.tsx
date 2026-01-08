"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'
import { useI18n } from '@/lib/hooks/useI18n'
import LGPDReport from './LGPDReport'
import DataViewer from './DataViewer'
import PIIViewer from './PIIViewer'
import ConsentimentoViewer from './ConsentimentoViewer'

type IngestaoListItem = {
  id: string
  fonte: string
  status: string
  confiabilidade_score: number
  data_ingestao: string
  consentimento_id?: string
}

type IngestaoListResponse = {
  items: IngestaoListItem[]
  total: number
  offset: number
  limit: number
}

type ViewMode = 'lgpd' | 'data' | 'pii' | 'consent'

export default function IngestaoTable() {
  const { t, locale } = useI18n()
  const [data, setData] = useState<IngestaoListItem[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('lgpd')
  const [actionMenuId, setActionMenuId] = useState<string | null>(null)

  const load = async () => {
    try {
      // Add timestamp to force cache bust
      const timestamp = Date.now()
      const res = await get<IngestaoListResponse>(`/ingestions?_t=${timestamp}`)
      console.log('Loaded ingestions:', res.items.length, 'items')
      setData(res.items)
    } catch (e) {
      console.error('Failed to load ingestions:', e)
    }
  }

  useEffect(() => { 
    // Initial load
    load() 
    
    // Listen for ingestion creation events for immediate update
    const handler = () => { 
      load()
      setTimeout(() => load(), 1000)
    }
    if (typeof window !== 'undefined') {
      window.addEventListener('ingestion:created', handler)
    }
    
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('ingestion:created', handler)
      }
    }
  }, [])

  const handleAction = (id: string, mode: ViewMode) => {
    if (mode === 'consent') {
      const item = data.find(it => it.id === id)
      if (item?.consentimento_id) {
        setSelectedId(item.consentimento_id)
      }
    } else {
      setSelectedId(id)
    }
    setViewMode(mode)
    setActionMenuId(null)
  }
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const localeCode = locale === 'pt-BR' ? 'pt-BR' : locale === 'es-ES' ? 'es-ES' : 'en-US'
    return date.toLocaleString(localeCode)
  }

  return (
    <>
      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-2">{t('ingestion:table.recent_ingestions')}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full border rounded">
            <thead>
              <tr className="bg-gray-50">
                <th className="p-2 text-left">{t('ingestion:table.id')}</th>
                <th className="p-2 text-left">{t('ingestion:table.source')}</th>
                <th className="p-2 text-left">{t('ingestion:table.status')}</th>
                <th className="p-2 text-left">{t('ingestion:table.lgpd_score')}</th>
                <th className="p-2 text-left">{t('ingestion:table.created_at')}</th>
                <th className="p-2 text-left">{t('ingestion:table.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {data.map((it) => (
                <tr key={it.id} className="border-t hover:bg-gray-50">
                  <td className="p-2 text-xs font-mono">{it.id.slice(0, 8)}...</td>
                  <td className="p-2 font-medium">{t(`ingestion:source.${it.fonte}`)}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      it.status === 'concluida' ? 'bg-green-100 text-green-800' :
                      it.status === 'processando' ? 'bg-blue-100 text-blue-800' :
                      it.status === 'erro' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {t(`ingestion:status.${it.status}`)}
                    </span>
                  </td>
                  <td className="p-2">
                    <span className="font-semibold">{it.confiabilidade_score}%</span>
                  </td>
                  <td className="p-2 text-sm text-gray-600">
                    {formatDate(it.data_ingestao)}
                  </td>
                  <td className="p-2">
                    <button
                      onClick={() => setActionMenuId(actionMenuId === it.id ? null : it.id)}
                      className="px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 text-sm font-medium"
                    >
                      {t('ingestion:action.actions_button')} ▾
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data.length === 0 && (
          <p className="text-center text-gray-500 py-8">{t('ingestion:table.no_data')}</p>
        )}
      </div>

      {/* Modal de Ações - Mobile First */}
      {actionMenuId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end sm:items-center justify-center z-50 p-4">
          <div className="bg-white w-full sm:w-96 rounded-t-lg sm:rounded-lg p-4 sm:p-6 max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">{t('ingestion:table.actions_menu')}</h3>
              <button
                onClick={() => setActionMenuId(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="space-y-2">
              <button
                onClick={() => handleAction(actionMenuId, 'data')}
                className="w-full text-left px-4 py-3 rounded hover:bg-gray-100 flex items-center gap-3 transition-colors"
              >
                <span className="text-xl">📊</span>
                <div>
                  <div className="font-medium">{t('ingestion:action.view_data')}</div>
                  <div className="text-xs text-gray-500">{t('ingestion:action.view_data_desc')}</div>
                </div>
              </button>

              <button
                onClick={() => handleAction(actionMenuId, 'pii')}
                className="w-full text-left px-4 py-3 rounded hover:bg-gray-100 flex items-center gap-3 transition-colors"
              >
                <span className="text-xl">🔒</span>
                <div>
                  <div className="font-medium">{t('ingestion:action.view_pii')}</div>
                  <div className="text-xs text-gray-500">{t('ingestion:action.view_pii_desc')}</div>
                </div>
              </button>

              <button
                onClick={() => handleAction(actionMenuId, 'lgpd')}
                className="w-full text-left px-4 py-3 rounded hover:bg-gray-100 flex items-center gap-3 transition-colors"
              >
                <span className="text-xl">📋</span>
                <div>
                  <div className="font-medium">{t('ingestion:action.lgpd_report')}</div>
                  <div className="text-xs text-gray-500">{t('ingestion:action.lgpd_report_desc')}</div>
                </div>
              </button>

              {(() => {
                const item = data.find(it => it.id === actionMenuId)
                return item?.consentimento_id && (
                  <button
                    onClick={() => handleAction(actionMenuId, 'consent')}
                    className="w-full text-left px-4 py-3 rounded hover:bg-gray-100 flex items-center gap-3 transition-colors"
                  >
                    <span className="text-xl">✓</span>
                    <div>
                      <div className="font-medium">{t('ingestion:action.view_consent')}</div>
                      <div className="text-xs text-gray-500">{t('ingestion:action.view_consent_desc')}</div>
                    </div>
                  </button>
                )
              })()}
            </div>
          </div>
        </div>
      )}

      {selectedId && viewMode === 'lgpd' && (
        <LGPDReport ingestaoId={selectedId} onClose={() => setSelectedId(null)} />
      )}
      {selectedId && viewMode === 'data' && (
        <DataViewer ingestaoId={selectedId} onClose={() => setSelectedId(null)} />
      )}
      {selectedId && viewMode === 'pii' && (
        <PIIViewer ingestaoId={selectedId} onClose={() => setSelectedId(null)} />
      )}
      {selectedId && viewMode === 'consent' && (
        <ConsentimentoViewer consentimentoId={selectedId} onClose={() => setSelectedId(null)} />
      )}
    </>
  )
}
