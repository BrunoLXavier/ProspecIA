"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'

type Props = {
  ingestaoId: string
  onClose: () => void
}

type IngestaoDetail = {
  id: string
  fonte: string
  dados_brutos_sample?: any[]
  total_registros: number
  registros_validos: number
  registros_invalidos: number
}

export default function DataViewer({ ingestaoId, onClose }: Props) {
  const [data, setData] = useState<IngestaoDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await get<IngestaoDetail>(`/ingestions/${ingestaoId}`)
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
          <p className="text-center text-gray-600">Carregando dados...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-6xl w-full">
          <p className="text-center text-red-600">Erro ao carregar dados</p>
          <button onClick={onClose} className="mt-4 btn-primary mx-auto block">Fechar</button>
        </div>
      </div>
    )
  }

  const sampleData = data.dados_brutos_sample || []
  const columns = sampleData.length > 0 ? Object.keys(sampleData[0]) : []

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 max-w-6xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-primary-600">Visualização de Dados</h2>
            <p className="text-sm text-gray-500">Ingestão: {ingestaoId.slice(0, 8)}...</p>
            <p className="text-sm text-gray-600 mt-2">
              Fonte: <span className="font-medium">{data.fonte.toUpperCase()}</span>
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-600 font-medium">Total de Registros</p>
            <p className="text-3xl font-bold text-blue-700">{data.total_registros}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm text-green-600 font-medium">Registros Válidos</p>
            <p className="text-3xl font-bold text-green-700">{data.registros_validos}</p>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <p className="text-sm text-red-600 font-medium">Registros Inválidos</p>
            <p className="text-3xl font-bold text-red-700">{data.registros_invalidos}</p>
          </div>
        </div>

        {/* Amostra de Dados */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">
            Amostra de Dados (Primeiros {sampleData.length} registros)
          </h3>
          {sampleData.length > 0 ? (
            <div className="overflow-x-auto border rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {columns.map((col) => (
                      <th
                        key={col}
                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {sampleData.map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      {columns.map((col) => (
                        <td key={col} className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                          {typeof row[col] === 'object' ? JSON.stringify(row[col]) : String(row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8 bg-gray-50 rounded-lg">
              Nenhuma amostra de dados disponível
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t">
          <button onClick={onClose} className="btn-primary">Fechar</button>
        </div>
      </div>
    </div>
  )
}
