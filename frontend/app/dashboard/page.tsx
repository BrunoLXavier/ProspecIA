import IngestaoForm from '@/components/features/IngestaoForm'
import IngestaoTable from '@/components/features/IngestaoTable'

export default function DashboardPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-start pt-6 sm:pt-12 lg:pt-24 px-6 sm:px-12 lg:px-24 pb-24">
      <div className="w-full max-w-5xl">
        <h1 className="text-4xl font-bold text-primary-600 mb-4">Ingestão de Dados</h1>
        <p className="text-secondary-600 mb-6">Envie arquivos, acompanhe ingestões e visualize linhagem.</p>
        {/* Components */}
        {/** @ts-ignore **/}
        <IngestaoForm />
        {/** @ts-ignore **/}
        <IngestaoTable />
        <div className="mt-8">
          <a href="/" className="btn-primary">← Voltar para Home</a>
        </div>
      </div>
    </main>
  )
}
