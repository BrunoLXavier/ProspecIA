"use client"

import { useState } from 'react'
import { post } from '@/lib/api/client'
import toast from 'react-hot-toast'

const fontes = ["rais","ibge","inpi","finep","bndes","customizada"] as const
const metodos = ["batch_upload","api_pull","manual","scheduled"] as const

type IngestaoCreateResponse = {
  id: string
  fonte: string
  status: string
  arquivo_storage_path?: string
  qr_code_base64?: string
  confiabilidade_score: number
  data_ingestao: string
}

export default function IngestaoForm() {
  const [file, setFile] = useState<File | null>(null)
  const [fonte, setFonte] = useState<typeof fontes[number]>("rais")
  const [metodo, setMetodo] = useState<typeof metodos[number]>("batch_upload")
  const [descricao, setDescricao] = useState("")
  const [qrCode, setQrCode] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      toast.error('Selecione um arquivo para enviar')
      return
    }

    try {
      const form = new FormData()
      form.append('file', file)

      const url = `/ingestions?fonte=${fonte}&metodo=${metodo}` + (descricao ? `&descricao=${encodeURIComponent(descricao)}` : '')
      const res = await post<IngestaoCreateResponse>(url, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      setQrCode(res.qr_code_base64 || null)
      toast.success('Ingestão criada com sucesso')
    } catch (err: any) {
      console.error(err)
      toast.error(err?.response?.data?.detail || 'Falha ao criar ingestão')
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4 border rounded p-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium">Fonte</label>
          <select value={fonte} onChange={(e) => setFonte(e.target.value as any)} className="mt-1 w-full border rounded p-2">
            {fontes.map(f => (<option key={f} value={f}>{f.toUpperCase()}</option>))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium">Método</label>
          <select value={metodo} onChange={(e) => setMetodo(e.target.value as any)} className="mt-1 w-full border rounded p-2">
            {metodos.map(m => (<option key={m} value={m}>{m.replace('_',' ').toUpperCase()}</option>))}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium">Descrição</label>
        <input value={descricao} onChange={(e) => setDescricao(e.target.value)} className="mt-1 w-full border rounded p-2" />
      </div>
      <div>
        <label className="block text-sm font-medium">Arquivo</label>
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="mt-1" />
      </div>
      <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Enviar</button>

      {qrCode && (
        <div className="mt-4">
          <p className="text-sm">QR Code de rastreamento:</p>
          <img src={`data:image/png;base64,${qrCode}`} alt="QR Code" className="mt-2 w-40 h-40" />
        </div>
      )}
    </form>
  )
}
