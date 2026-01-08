"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'

type Props = {
  ingestaoId: string
  onClose: () => void
}

type PIIData = {
  campo: string
  tipo_pii: string
  ocorrencias: number
  exemplos_mascarados: string[]
  nivel_sensibilidade: 'baixo' | 'medio' | 'alto'
}

type PIIReport = {
  total_pii_encontrados: number
  por_tipo: Record<string, number>
  detalhes: PIIData[]
}

export default function PIIViewer({ ingestaoId, onClose }: Props) {
  const [data, setData] = useState<PIIReport | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await get<PIIReport>(`/ingestions/${ingestaoId}/pii`)
        setData(res)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [ingestaoId])

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-6xl w-full max-h-[90vh] overflow-auto">
          <p className="text-center text-gray-600">Carregando dados PII...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-6xl w-full">
          <p className="text-center text-red-600">Erro ao carregar dados PII</p>
          <button onClick={onClose} className="mt-4 btn-primary mx-auto block">Fechar</button>
        </div>
      </div>
    )
  }

  const getSensibilidadeColor = (nivel: string) => {
    switch (nivel) {
      case 'alto': return 'bg-red-100 text-red-700 border-red-300'
      case 'medio': return 'bg-yellow-100 text-yellow-700 border-yellow-300'
      case 'baixo': return 'bg-green-100 text-green-700 border-green-300'
      default: return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 max-w-6xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-primary-600">Dados PII Identificados</h2>
            <p className="text-sm text-gray-500">Ingestão: {ingestaoId.slice(0, 8)}...</p>
            <p className="text-sm text-gray-600 mt-2">
              Total de dados sensíveis detectados: <span className="font-bold text-red-600">{data.total_pii_encontrados}</span>
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>

        {/* Resumo por Tipo */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Distribuição por Tipo de PII</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(data.por_tipo).map(([tipo, count]) => (
              <div key={tipo} className="bg-gradient-to-br from-primary-50 to-primary-100 p-4 rounded-lg border border-primary-200">
                <p className="text-sm text-primary-600 font-medium uppercase">{tipo}</p>
                <p className="text-2xl font-bold text-primary-700">{count}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Detalhes por Campo */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Detalhes por Campo</h3>
          <div className="space-y-4">
            {data.detalhes.map((item, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-semibold text-lg text-gray-900">{item.campo}</h4>
                    <div className="flex gap-2 mt-1">
                      <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                        {item.tipo_pii}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium border ${getSensibilidadeColor(item.nivel_sensibilidade)}`}>
                        Sensibilidade: {item.nivel_sensibilidade.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-900">{item.ocorrencias}</p>
                    <p className="text-xs text-gray-500">ocorrências</p>
                  </div>
                </div>

                {/* Exemplos Mascarados */}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Exemplos (mascarados):</p>
                  <div className="bg-gray-50 p-3 rounded border border-gray-200">
                    <div className="flex flex-wrap gap-2">
                      {item.exemplos_mascarados.map((exemplo, i) => (
                        <code key={i} className="text-xs bg-white px-2 py-1 rounded border border-gray-300 font-mono">
                          {exemplo}
                        </code>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alertas de Conformidade */}
        {data.total_pii_encontrados > 0 && (
          <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-900">
              <span className="font-bold">⚠ Atenção:</span> Foram identificados dados pessoais sensíveis nesta ingestão. 
              Certifique-se de que o consentimento adequado foi obtido e que as medidas de segurança necessárias estão em vigor.
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t">
          <button onClick={onClose} className="btn-primary">Fechar</button>
        </div>
      </div>
    </div>
  )
}
