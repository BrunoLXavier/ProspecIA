"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'

type PIITypeStat = {
  type: string
  count: number
  samples: string[]
}

type ConsentRecord = {
  tipo_consentimento: string
  finalidade: string
  status: string
  data_consentimento?: string
  data_revogacao?: string
}

type LGPDReportResponse = {
  ingestao_id: string
  compliance_score: number
  pii_types_detected: { [key: string]: number }
  total_pii_instances: number
  pii_details: PIITypeStat[]
  consent_status: string
  consent_records: ConsentRecord[]
  recommendations: string[]
  risk_level: string
  lgpd_articles_applicable: string[]
  data_analysis: string
}

type Props = {
  ingestaoId: string
  onClose: () => void
}

export default function LGPDReport({ ingestaoId, onClose }: Props) {
  const [data, setData] = useState<LGPDReportResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await get<LGPDReportResponse>(`/ingestions/${ingestaoId}/lgpd-report`)
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
        <div className="bg-white rounded-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-auto">
          <p className="text-center text-gray-600">Carregando relatório LGPD...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-4xl w-full">
          <p className="text-center text-red-600">Erro ao carregar relatório</p>
          <button onClick={onClose} className="mt-4 btn-primary mx-auto block">Fechar</button>
        </div>
      </div>
    )
  }

  const riskColor = {
    CRÍTICO: 'text-red-600 bg-red-50',
    ALTO: 'text-orange-600 bg-orange-50',
    MÉDIO: 'text-yellow-600 bg-yellow-50',
    BAIXO: 'text-green-600 bg-green-50'
  }[data.risk_level] || 'text-gray-600 bg-gray-50'

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-primary-600">Relatório LGPD</h2>
            <p className="text-sm text-gray-500">Ingestão: {ingestaoId.slice(0, 8)}...</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>

        {/* Compliance Score */}
        <div className="mb-6 p-4 bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-primary-700 font-medium">Score de Conformidade LGPD</p>
              <p className="text-4xl font-bold text-primary-600">{data.compliance_score}%</p>
            </div>
            <div className={`px-4 py-2 rounded-full ${riskColor} font-semibold`}>
              Risco: {data.risk_level}
            </div>
          </div>
        </div>

        {/* PII Detectado */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Dados Pessoais Identificados</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {data.pii_details.map((pii) => (
              <div key={pii.type} className="border rounded-lg p-4 bg-gray-50">
                <p className="text-sm text-gray-600 font-medium">{pii.type.toUpperCase()}</p>
                <p className="text-2xl font-bold text-primary-600">{pii.count}</p>
                {pii.samples.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-gray-500 mb-1">Exemplos (mascarados):</p>
                    {pii.samples.slice(0, 2).map((sample, idx) => (
                      <p key={idx} className="text-xs font-mono bg-white px-2 py-1 rounded mb-1">{sample}</p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Total: {data.total_pii_instances} instâncias de dados pessoais detectadas
          </p>
        </div>

        {/* Consentimentos */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Status de Consentimento</h3>
          <div className={`p-4 rounded-lg ${
            data.consent_status === 'valid' ? 'bg-green-50 border border-green-200' :
            data.consent_status === 'missing' ? 'bg-yellow-50 border border-yellow-200' :
            'bg-red-50 border border-red-200'
          }`}>
            <p className="font-medium mb-2">
              {data.consent_status === 'valid' ? '✓ Consentimento Válido' :
               data.consent_status === 'missing' ? '⚠ Consentimento Ausente' :
               '✗ Consentimento Revogado'}
            </p>
            {data.consent_records.length > 0 ? (
              <div className="space-y-2 mt-2">
                {data.consent_records.map((consent, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border">
                    <p className="text-sm"><strong>Tipo:</strong> {consent.tipo_consentimento}</p>
                    <p className="text-sm"><strong>Finalidade:</strong> {consent.finalidade}</p>
                    <p className="text-sm"><strong>Status:</strong> {consent.status}</p>
                    {consent.data_consentimento && (
                      <p className="text-xs text-gray-500">Concedido em: {new Date(consent.data_consentimento).toLocaleString()}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-600">Nenhum registro de consentimento encontrado</p>
            )}
          </div>
        </div>

        {/* Artigos LGPD Aplicáveis */}
        {data.lgpd_articles_applicable.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Artigos LGPD Aplicáveis</h3>
            <div className="flex flex-wrap gap-2">
              {data.lgpd_articles_applicable.map((article) => (
                <span key={article} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                  {article}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Recomendações */}
        {data.recommendations.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Recomendações</h3>
            <ul className="space-y-2">
              {data.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-primary-600 mr-2">•</span>
                  <span className="text-sm text-gray-700">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Análise */}
        {data.data_analysis && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Análise Detalhada</h3>
            <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
              {data.data_analysis}
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
