"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'

type LinhagemNode = { id: string; type: string; label: string; properties: Record<string, any> }
type LinhagemEdge = { source: string; target: string; type: string; properties: Record<string, any> }

type LinhagemResponse = {
  ingestao_id: string
  nodes: LinhagemNode[]
  edges: LinhagemEdge[]
  dados_brutos_sample?: string | null
  transformacoes: string[]
  confiabilidade_score: number
  data_ingestao: string
}

export default function LinhagemTimeline({ ingestaoId }: { ingestaoId: string }) {
  const [data, setData] = useState<LinhagemResponse | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await get<LinhagemResponse>(`/ingestions/${ingestaoId}/lineage`)
        setData(res)
      } catch (e) {
        console.error(e)
      }
    }
    load()
  }, [ingestaoId])

  if (!data) return null

  return (
    <div className="mt-6">
      <h2 className="text-xl font-semibold mb-2">Linhagem de Dados</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="border rounded p-3">
          <h3 className="font-medium">Nós</h3>
          <ul className="text-sm space-y-1">
            {data.nodes.map((n) => (
              <li key={n.id}>
                <span className="font-semibold">[{n.type}]</span> {n.label}
              </li>
            ))}
          </ul>
        </div>
        <div className="border rounded p-3">
          <h3 className="font-medium">Transformações</h3>
          <ul className="text-sm list-disc ml-6">
            {data.transformacoes.map((t) => (<li key={t}>{t}</li>))}
          </ul>
        </div>
      </div>
      {data.dados_brutos_sample && (
        <div className="border rounded p-3 mt-4">
          <h3 className="font-medium">Amostra de Dados Brutos</h3>
          <pre className="text-sm whitespace-pre-wrap">{data.dados_brutos_sample}</pre>
        </div>
      )}
    </div>
  )
}
