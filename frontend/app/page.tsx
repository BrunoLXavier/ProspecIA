import Link from 'next/link'

export default function HomePage() {
  const docsUrl = process.env.NEXT_PUBLIC_API_URL
    ? `${process.env.NEXT_PUBLIC_API_URL}/docs`
    : 'http://localhost:8000/docs'

  return (
    <main className="flex min-h-screen flex-col items-center justify-start pt-6 sm:pt-12 lg:pt-24 px-6 sm:px-12 lg:px-24">
      <div className="z-10 w-full max-w-5xl font-mono text-sm flex items-center justify-center">
        <h1 className="text-4xl font-bold text-primary-600">ProspecIA</h1>
      </div>

      <div className="relative flex place-items-center mt-16">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-secondary-900 mb-4">
            Sistema de Prospecção e Gestão de Inovação
          </h2>
          <p className="text-secondary-600 mb-8 max-w-2xl">
            Plataforma com IA Responsável para gestão de fomento, portfólio institucional,
            CRM de inovação e pipeline de oportunidades.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link href="/dashboard" className="btn-primary">
              Acessar Dashboard
            </Link>
            <a href={docsUrl} className="btn-secondary" target="_blank" rel="noreferrer">Documentação</a>
          </div>
          
          <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl">
            <div className="card text-left">
              <h3 className="text-lg font-semibold text-primary-600 mb-2">
                🎯 Gestão Completa
              </h3>
              <p className="text-sm text-secondary-600">
                Fomento, portfólio, CRM e pipeline integrados em uma única plataforma.
              </p>
            </div>
            
            <div className="card text-left">
              <h3 className="text-lg font-semibold text-primary-600 mb-2">
                🤖 IA Responsável
              </h3>
              <p className="text-sm text-secondary-600">
                Sugestões com explicabilidade e humano sempre no controle.
              </p>
            </div>
            
            <div className="card text-left">
              <h3 className="text-lg font-semibold text-primary-600 mb-2">
                🔒 LGPD Compliance
              </h3>
              <p className="text-sm text-secondary-600">
                Governança de dados e auditoria completa desde o início.
              </p>
            </div>
          </div>
        </div>
      </div>

      <footer className="mt-16 text-center text-sm text-secondary-500">
        <p>Wave 0 - Fundação (TRL 3-4)</p>
        <p className="mt-2">Versão 1.0.0 | Janeiro 2026</p>
      </footer>
    </main>
  )
}
