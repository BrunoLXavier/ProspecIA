"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'
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
  const [data, setData] = useState<IngestaoListItem[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('lgpd')
  const [actionMenuId, setActionMenuId] = useState<string | null>(null)

  const load = async () => {
    try {
      const res = await get<IngestaoListResponse>('/ingestions')
      setData(res.items)
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => { load() }, [])

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

  return (
    <>
      <div className="mt-6">
        <h2 className="text-xl font-semibold mb-2">Ingestões Recentes</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full border rounded">
            <thead>
              <tr className="bg-gray-50">
                <th className="p-2 text-left">ID</th>
                <th className="p-2 text-left">Fonte</th>
                <th className="p-2 text-left">Status</th>
                <th className="p-2 text-left">Score</th>
                <th className="p-2 text-left">Data</th>
                <th className="p-2 text-left">Ações</th>
              </tr>
            </thead>
            <tbody>
              {data.map((it) => (
                <tr key={it.id} className="border-t hover:bg-gray-50">
                  <td className="p-2 text-xs font-mono">{it.id.slice(0, 8)}...</td>
                  <td className="p-2 font-medium">{it.fonte.toUpperCase()}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      it.status === 'concluida' ? 'bg-green-100 text-green-800' :
                      it.status === 'processando' ? 'bg-blue-100 text-blue-800' :
                      it.status === 'erro' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {it.status}
                    </span>
                  </td>
                  <td className="p-2">
                    <span className="font-semibold">{it.confiabilidade_score}%</span>
                  </td>
                  <td className="p-2 text-sm text-gray-600">
                    {new Date(it.data_ingestao).toLocaleString('pt-BR')}
                  </td>
                  <td className="p-2">
                    <button
                      onClick={() => setActionMenuId(actionMenuId === it.id ? null : it.id)}
                      className="px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 text-sm font-medium"
                    >
                      Ações ▾
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data.length === 0 && (
          <p className="text-center text-gray-500 py-8">Nenhuma ingestão encontrada</p>
        )}
      </div>

      {/* Modal de Ações - Mobile First */}
      {actionMenuId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end sm:items-center justify-center z-50 p-4">
          <div className="bg-white w-full sm:w-96 rounded-t-lg sm:rounded-lg p-4 sm:p-6 max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Ações da Ingestão</h3>
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
                  <div className="font-medium">Ver Dados</div>
                  <div className="text-xs text-gray-500">Amostra dos dados ingeridos</div>
                </div>
              </button>

              <button
                onClick={() => handleAction(actionMenuId, 'pii')}
                className="w-full text-left px-4 py-3 rounded hover:bg-gray-100 flex items-center gap-3 transition-colors"
              >
                <span className="text-xl">🔒</span>
                <div>
                  <div className="font-medium">Ver Dados PII</div>
                  <div className="text-xs text-gray-500">Dados sensíveis detectados</div>
                </div>
              </button>

              <button
                onClick={() => handleAction(actionMenuId, 'lgpd')}
                className="w-full text-left px-4 py-3 rounded hover:bg-gray-100 flex items-center gap-3 transition-colors"
              >
                <span className="text-xl">📋</span>
                <div>
                  <div className="font-medium">Ver Relatório LGPD</div>
                  <div className="text-xs text-gray-500">Análise de conformidade</div>
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
                      <div className="font-medium">Ver Consentimento</div>
                      <div className="text-xs text-gray-500">Detalhes do consentimento</div>
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
