"use client"

import { useState } from 'react'
import { post } from '@/lib/api/client'
import toast from 'react-hot-toast'
import { useI18n } from '@/lib/hooks/useI18n'

const fontes = ["rais","ibge","inpi","finep","bndes","customizada"] as const
const metodos = ["batch_upload","api_pull","manual","scheduled"] as const

type IngestaoCreateResponse = {
  id: string
  fonte: string
  status: string
  arquivo_storage_path?: string
  confiabilidade_score: number
  data_ingestao: string
}

export default function IngestionForm({ onSubmit }: { onSubmit?: () => void }) {
  const { t } = useI18n()
  const [file, setFile] = useState<File | null>(null)
  const [fonte, setFonte] = useState<typeof fontes[number]>("rais")
  const [metodo, setMetodo] = useState<typeof metodos[number]>("batch_upload")
  const [descricao, setDescricao] = useState("")
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)

  const handleSubmit = async () => {
    console.log('[handleSubmit] Started!', { fileName: file?.name })
    
    if (!file) {
      toast.error(t('ingestion:message.select_file'))
      return
    }

    try {
      setUploading(true)
      setUploadProgress(0)
      
      const formData = new FormData()
      formData.append('file', file)

      const params = new URLSearchParams()
      params.append('fonte', fonte)
      params.append('metodo', metodo)
      if (descricao) params.append('descricao', descricao)

      const url = `/ingestions?${params.toString()}`

      console.log('[handleSubmit] Sending to:', url)
      const res = await post<IngestaoCreateResponse>(url, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt: any) => {
          const total = evt.total ?? file.size ?? 0
          if (total > 0) {
            const pct = Math.round((evt.loaded / total) * 100)
            setUploadProgress(Math.min(pct, 99))
          }
        },
      })

      console.log('[handleSubmit] Success!', { id: res.id })
      setUploadProgress(100)
      setUploading(false)
      toast.success(t('ingestion:message.upload_success'))
      
      window.dispatchEvent(new CustomEvent('ingestion:created', { detail: { id: res.id } }))
      
      setFile(null)
      setDescricao('')
      setUploadProgress(null)

      if (onSubmit) {
        onSubmit();
      }
    } catch (err: any) {
      console.error('[handleSubmit] Error:', err)
      setUploading(false)
      setUploadProgress(null)
      toast.error(err?.response?.data?.detail || t('ingestion:message.upload_error'))
    }
  }

  return (
    <div className="space-y-4 border rounded p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium">{t('ingestion:form.source_label')}</label>
          <select value={fonte} onChange={(e) => setFonte(e.target.value as any)} className="mt-1 w-full border rounded p-2">
            {fontes.map(f => (<option key={f} value={f}>{t(`ingestion:source.${f}`)}</option>))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium">{t('ingestion:form.method_label')}</label>
          <select value={metodo} onChange={(e) => setMetodo(e.target.value as any)} className="mt-1 w-full border rounded p-2">
            {metodos.map(m => (<option key={m} value={m}>{t(`ingestion:method.${m}`)}</option>))}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium">{t('ingestion:form.description_label')}</label>
        <input 
          value={descricao} 
          onChange={(e) => setDescricao(e.target.value)} 
          placeholder={t('ingestion:form.description_placeholder')}
          className="mt-1 w-full border rounded p-2" 
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-2">{t('ingestion.file')}</label>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="w-full" />
        {uploadProgress !== null && (
          <div className="mt-4">
            <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-blue-600 transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="mt-2 text-sm text-gray-600 font-medium">{t('ingestion:form.uploading')} {uploadProgress}%</p>
          </div>
        )}
      </div>
      <button
        type="button"
        onClick={handleSubmit}
        className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-60 hover:bg-blue-700"
        disabled={uploading}
      >
        {uploading ? t('ingestion:form.uploading') : t('ingestion:form.upload_button')}
      </button>
    </div>
  )
}
