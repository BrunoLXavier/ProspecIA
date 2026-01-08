"use client"

import { useEffect, useState } from 'react'
import { get } from '@/lib/api/client'

type Props = {
  consentimentoId: string
  onClose: () => void
}

type Consentimento = {
  id: string
  versao: number
  finalidade: string
  categorias_dados: string[]
  consentimento_dado: boolean
  data_consentimento?: string
  revogado: boolean
  data_revogacao?: string
  motivo_revogacao?: string
  origem_coleta: string
  consentimento_marketing: boolean
  consentimento_compartilhamento: boolean
  consentimento_analise: boolean
  base_legal: string
  data_expiracao?: string
}

export default function ConsentimentoViewer({ consentimentoId, onClose }: Props) {
  const [data, setData] = useState<Consentimento | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        // Note: This endpoint needs to be created in backend
        const res = await get<Consentimento>(`/consents/${consentimentoId}`)
        setData(res)
      } catch (e) {
        console.error(e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [consentimentoId])

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-auto">
          <p className="text-center text-gray-600">Carregando consentimento...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-4xl w-full">
          <p className="text-center text-red-600">Erro ao carregar consentimento</p>
          <button onClick={onClose} className="mt-4 btn-primary mx-auto block">Fechar</button>
        </div>
      </div>
    )
  }

  const isValid = data.consentimento_dado && !data.revogado

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-primary-600">Detalhes do Consentimento</h2>
            <p className="text-sm text-gray-500">ID: {consentimentoId.slice(0, 8)}... | Versão: {data.versao}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>

        {/* Status Badge */}
        <div className={`mb-6 p-4 rounded-lg ${
          isValid ? 'bg-green-50 border border-green-200' :
          data.revogado ? 'bg-red-50 border border-red-200' :
          'bg-yellow-50 border border-yellow-200'
        }`}>
          <p className="font-medium text-lg">
            {isValid ? '✓ Consentimento Válido e Ativo' :
             data.revogado ? '✗ Consentimento Revogado' :
             '⚠ Consentimento Não Concedido'}
          </p>
        </div>

        {/* Informações Principais */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Informações Básicas</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Finalidade</p>
                <p className="font-medium">{data.finalidade}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Base Legal</p>
                <p className="font-medium">{data.base_legal}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Origem da Coleta</p>
                <p className="font-medium">{data.origem_coleta}</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Datas</h3>
            <div className="space-y-3">
              {data.data_consentimento && (
                <div>
                  <p className="text-sm text-gray-600">Data de Consentimento</p>
                  <p className="font-medium">{new Date(data.data_consentimento).toLocaleString('pt-BR')}</p>
                </div>
              )}
              {data.data_revogacao && (
                <div>
                  <p className="text-sm text-gray-600">Data de Revogação</p>
                  <p className="font-medium text-red-600">{new Date(data.data_revogacao).toLocaleString('pt-BR')}</p>
                </div>
              )}
              {data.data_expiracao && (
                <div>
                  <p className="text-sm text-gray-600">Data de Expiração</p>
                  <p className="font-medium">{new Date(data.data_expiracao).toLocaleString('pt-BR')}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Categorias de Dados */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Categorias de Dados Abrangidas</h3>
          <div className="flex flex-wrap gap-2">
            {data.categorias_dados.map((cat) => (
              <span key={cat} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                {cat}
              </span>
            ))}
          </div>
        </div>

        {/* Permissões Granulares */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">Permissões Granulares</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className={`p-4 rounded-lg ${data.consentimento_marketing ? 'bg-green-50' : 'bg-gray-50'}`}>
              <p className="text-sm font-medium text-gray-700">Marketing</p>
              <p className={`text-lg font-bold ${data.consentimento_marketing ? 'text-green-600' : 'text-gray-400'}`}>
                {data.consentimento_marketing ? '✓ Permitido' : '✗ Não Permitido'}
              </p>
            </div>
            <div className={`p-4 rounded-lg ${data.consentimento_compartilhamento ? 'bg-green-50' : 'bg-gray-50'}`}>
              <p className="text-sm font-medium text-gray-700">Compartilhamento</p>
              <p className={`text-lg font-bold ${data.consentimento_compartilhamento ? 'text-green-600' : 'text-gray-400'}`}>
                {data.consentimento_compartilhamento ? '✓ Permitido' : '✗ Não Permitido'}
              </p>
            </div>
            <div className={`p-4 rounded-lg ${data.consentimento_analise ? 'bg-green-50' : 'bg-gray-50'}`}>
              <p className="text-sm font-medium text-gray-700">Análise</p>
              <p className={`text-lg font-bold ${data.consentimento_analise ? 'text-green-600' : 'text-gray-400'}`}>
                {data.consentimento_analise ? '✓ Permitido' : '✗ Não Permitido'}
              </p>
            </div>
          </div>
        </div>

        {/* Motivo de Revogação */}
        {data.revogado && data.motivo_revogacao && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">Motivo da Revogação</h3>
            <p className="p-4 bg-red-50 text-red-900 rounded-lg">{data.motivo_revogacao}</p>
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
