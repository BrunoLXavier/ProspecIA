"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'
import LGPDReport from './LGPDReport'

type IngestaoListItem = {
  id: string
  fonte: string
  status: string
  confiabilidade_score: number
  data_ingestao: string
}

type IngestaoListResponse = {
  items: IngestaoListItem[]
  total: number
  offset: number
  limit: number
}

export default function LGPDQuickAccess() {
  const [data, setData] = useState<IngestaoListItem[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await get<IngestaoListResponse>('/ingestions')
        setData(res.items)
      } catch (e) {
        console.error(e)
      }
    }
    load()
  }, [])

  if (!data.length) {
    return null
  }

  const latest = data[0]

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Relatório LGPD (Acesso Rápido)</h3>
        <button
          className="btn-primary"
          onClick={() => setSelectedId(latest.id)}
        >
          Ver LGPD da última ingestão
        </button>
      </div>
      <p className="text-sm text-gray-600 mt-1">
        Última ingestão: {latest.fonte.toUpperCase()} • Status: {latest.status} • Score: {latest.confiabilidade_score}%
      </p>

      {selectedId && (
        <LGPDReport ingestaoId={selectedId} onClose={() => setSelectedId(null)} />
      )}
    </div>
  )
}
