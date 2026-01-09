#!/usr/bin/env python3
"""
Script de Seed Data para Wave 1 - ProspecIA
Cria dados de exemplo para demonstração: ingestões, consentimentos, dados PII mascarados

Uso:
    python scripts/seed_wave1_data.py

Princípios:
- Clean Code: Funções pequenas e focadas
- SOLID: Single Responsibility para cada função seed
- Dados realistas para demo convincente
"""
import asyncio
import sys
import uuid
from datetime import datetime, timedelta, UTC
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.infrastructure.config.settings import get_settings
from app.domain.models.ingestion import (
    Ingestion,
    IngestionSource,
    IngestionMethod,
    IngestionStatus,
)
from app.domain.models.consent import Consentimento


# ============================================
# Configuração
# ============================================

settings = get_settings()

# Database connection
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ============================================
# Dados de Exemplo
# ============================================

TENANT_ID = "nacional"
USER_ID = "admin-seed-script"
USER_UUID = uuid.UUID("00000000-0000-0000-0000-000000000123")

CONSENTIMENTOS_EXEMPLO = [
    {
        "titular_id": uuid.uuid4(),
        "finalidade": "Análise de dados de folha de pagamento para insights estratégicos",
        "categorias_dados": ["nome", "cpf", "salario", "cargo"],
        "consentimento_dado": True,
        "base_legal": "Art. 7º, V - Execução de contrato",
    },
    {
        "titular_id": uuid.uuid4(),
        "finalidade": "Processamento de dados de pesquisa para publicação científica",
        "categorias_dados": ["nome", "email", "telefone", "area_pesquisa"],
        "consentimento_dado": True,
        "base_legal": "Art. 7º, IX - Legítimo interesse",
    },
    {
        "titular_id": uuid.uuid4(),
        "finalidade": "Análise de viabilidade técnica para matching com fontes de fomento",
        "categorias_dados": ["cnpj", "razao_social", "setor", "faturamento"],
        "consentimento_dado": True,
        "base_legal": "Art. 7º, VI - Exercício regular de direitos",
    },
]

INGESTOES_EXEMPLO = [
    {
        "fonte": IngestionSource.RAIS,
        "metodo": IngestionMethod.BATCH_UPLOAD,
        "confiabilidade_score": 92,
        "status": IngestionStatus.CONCLUIDA,
        "arquivo_path": "ingestoes/2026/01/rais_sp_Q4_2025.csv",
        "pii_detectado": {
            "cpf": ["123.456.789-00", "987.654.321-00"],
            "email": ["funcionario1@empresa.com", "funcionario2@empresa.com"],
            "telefone": ["(11) 98765-4321"],
        },
        "lgpd_validado": True,
        "compliance_score": 95,
        "descricao": "Dados RAIS Q4 2025 - São Paulo (10.000 registros)",
        "total_registros": 10000,
        "registros_validos": 9800,
        "registros_invalidos": 200,
        "dados_sample": [
            {"cpf": "***.***.789-**", "nome": "João S***", "cargo": "Analista", "salario": 5500.00, "empresa": "Tech Solutions SP"},
            {"cpf": "***.***.321-**", "nome": "Maria P***", "cargo": "Desenvolvedora", "salario": 7800.00, "empresa": "Inovação Digital"},
            {"cpf": "***.***.654-**", "nome": "Carlos M***", "cargo": "Gerente", "salario": 12000.00, "empresa": "Consultoria Tech"},
        ],
    },
    {
        "fonte": IngestionSource.IBGE,
        "metodo": IngestionMethod.API_PULL,
        "confiabilidade_score": 98,
        "status": IngestionStatus.CONCLUIDA,
        "arquivo_path": "ingestoes/2026/01/ibge_censo_empresarial_sp_2025.json",
        "pii_detectado": {
            "cnpj": ["12.345.678/0001-90", "98.765.432/0001-10"],
        },
        "lgpd_validado": True,
        "compliance_score": 100,
        "descricao": "Censo Empresarial IBGE - SP 2025 (5.000 empresas)",
        "total_registros": 5000,
        "registros_validos": 4998,
        "registros_invalidos": 2,
        "dados_sample": [
            {"cnpj": "12.345.678/0001-90", "razao_social": "Indústria ABC Ltda", "setor": "Manufatura", "porte": "Médio", "faturamento_anual": 15000000},
            {"cnpj": "98.765.432/0001-10", "razao_social": "Comércio XYZ SA", "setor": "Varejo", "porte": "Grande", "faturamento_anual": 45000000},
            {"cnpj": "55.444.333/0001-22", "razao_social": "Serviços Tech ME", "setor": "Tecnologia", "porte": "Pequeno", "faturamento_anual": 800000},
        ],
    },
    {
        "fonte": IngestionSource.INPI,
        "metodo": IngestionMethod.BATCH_UPLOAD,
        "confiabilidade_score": 85,
        "status": IngestionStatus.PENDENTE,
        "arquivo_path": "ingestoes/2026/01/inpi_patentes_saude_2025.xlsx",
        "pii_detectado": {
            "nome": ["Dr. João Silva", "Dra. Maria Santos"],
            "email": ["joao.silva@instituto.br"],
        },
        "lgpd_validado": False,
        "compliance_score": 75,
        "descricao": "Patentes na área de Saúde - INPI 2025 (1.200 registros) - Aguardando validação LGPD",
        "total_registros": 1200,
        "registros_validos": 0,
        "registros_invalidos": 0,
        "dados_sample": [
            {"numero_patente": "BR1020250001234", "titulo": "Dispositivo de diagnóstico por imagem", "inventor": "Dr. João S***", "area": "Equipamentos Médicos", "ano_deposito": 2024},
            {"numero_patente": "BR1020250005678", "titulo": "Método de análise genética", "inventor": "Dra. Maria S***", "area": "Biotecnologia", "ano_deposito": 2024},
        ],
    },
    {
        "fonte": IngestionSource.FINEP,
        "metodo": IngestionMethod.MANUAL,
        "confiabilidade_score": 88,
        "status": IngestionStatus.CONCLUIDA,
        "arquivo_path": "ingestoes/2026/01/finep_projetos_aprovados_2024.csv",
        "pii_detectado": {
            "cnpj": ["45.678.901/0001-23"],
            "email": ["contato@startup-ia.com"],
        },
        "lgpd_validado": True,
        "compliance_score": 90,
        "descricao": "Projetos FINEP aprovados em 2024 - Área IA/ML (300 projetos)",
        "total_registros": 300,
        "registros_validos": 298,
        "registros_invalidos": 2,
        "dados_sample": [
            {"cnpj": "45.678.901/0001-23", "projeto": "IA para diagnóstico médico", "area": "Saúde Digital", "valor_aprovado": 850000, "prazo_meses": 24},
            {"cnpj": "11.222.333/0001-44", "projeto": "Machine Learning para agronegócio", "area": "AgTech", "valor_aprovado": 650000, "prazo_meses": 18},
            {"cnpj": "99.888.777/0001-55", "projeto": "Blockchain para supply chain", "area": "Logística", "valor_aprovado": 1200000, "prazo_meses": 30},
        ],
    },
    {
        "fonte": IngestionSource.BNDES,
        "metodo": IngestionMethod.SCHEDULED,
        "confiabilidade_score": 95,
        "status": IngestionStatus.FALHA,
        "arquivo_path": "ingestoes/2026/01/bndes_fomento_energia_2025.csv",
        "pii_detectado": {},
        "lgpd_validado": False,
        "compliance_score": 0,
        "erros_encontrados": [
            {
                "tipo": "FORMATO_INVALIDO",
                "mensagem": "Coluna 'valor_financiamento' contém valores não numéricos",
                "linha": 450,
            },
            {
                "tipo": "CONEXAO_API",
                "mensagem": "Timeout ao conectar com API BNDES após 30s",
            },
        ],
        "descricao": "Linhas de fomento BNDES - Energia 2025 (ERRO: formato inválido)",
        "total_registros": 0,
        "registros_validos": 0,
        "registros_invalidos": 0,
        "dados_sample": [],  # Vazio porque ingestão falhou
    },
    {
        "fonte": IngestionSource.CUSTOMIZADA,
        "metodo": IngestionMethod.BATCH_UPLOAD,
        "confiabilidade_score": 80,
        "status": IngestionStatus.CONCLUIDA,
        "arquivo_path": "ingestoes/2026/01/clientes_importados_2025.csv",
        "pii_detectado": {
            "cpf": ["111.222.333-44", "555.666.777-88"],
            "email": ["cliente1@email.com", "cliente2@email.com"],
        },
        "lgpd_validado": True,
        "compliance_score": 85,
        "descricao": "Dados de clientes importados via upload - Cadastro 2025 (2.500 registros)",
        "total_registros": 2500,
        "registros_validos": 2450,
        "registros_invalidos": 50,
        "dados_sample": [
            {"cpf": "111.222.333-**", "nome": "Cliente A***", "email": "cliente1@***", "cidade": "São Paulo", "estado": "SP", "segmento": "Varejo"},
            {"cpf": "555.666.777-**", "nome": "Cliente B***", "email": "cliente2@***", "cidade": "Rio de Janeiro", "estado": "RJ", "segmento": "Serviços"},
            {"cpf": "999.888.777-**", "nome": "Cliente C***", "email": "cliente3@***", "cidade": "Belo Horizonte", "estado": "MG", "segmento": "Indústria"},
        ],
    },
    {
        "fonte": IngestionSource.CUSTOMIZADA,
        "metodo": IngestionMethod.BATCH_UPLOAD,
        "confiabilidade_score": 75,
        "status": IngestionStatus.PROCESSANDO,
        "arquivo_path": "ingestoes/2026/01/transacoes_janeiro_2026.xlsx",
        "pii_detectado": {
            "email": ["usuario1@empresa.com", "usuario2@empresa.com"],
        },
        "lgpd_validado": False,
        "compliance_score": 70,
        "descricao": "Dados de transações de janeiro/2026 - Em processamento (8.900 registros)",
        "total_registros": 8900,
        "registros_validos": 0,
        "registros_invalidos": 0,
        "dados_sample": [
            {"data": "2026-01-01", "tipo": "venda", "valor": 1500.00, "categoria": "Eletrônicos", "status": "confirmado"},
            {"data": "2026-01-02", "tipo": "venda", "valor": 2300.50, "categoria": "Vestuário", "status": "confirmado"},
            {"data": "2026-01-03", "tipo": "devolução", "valor": 450.00, "categoria": "Eletrônicos", "status": "processando"},
        ],
    },
]


# ============================================
# Funções de Seed
# ============================================


async def seed_consentimentos(session: AsyncSession) -> list[Consentimento]:
    """
    Cria consentimentos de exemplo
    
    Returns:
        Lista de consentimentos criados
    """
    print("\n📋 Criando consentimentos de exemplo...")
    
    consentimentos = []
    for idx, dados in enumerate(CONSENTIMENTOS_EXEMPLO, 1):
        consentimento = Consentimento(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            titular_id=dados["titular_id"],
            finalidade=dados["finalidade"],
            categorias_dados=dados["categorias_dados"],
            base_legal=dados["base_legal"],
            consentimento_dado=dados["consentimento_dado"],
            data_consentimento=(datetime.now(datetime.UTC) - timedelta(days=30 - idx)),
            versao=1,
            coletado_por=USER_UUID,
        )
        session.add(consentimento)
        consentimentos.append(consentimento)
        print(f"  ✓ Consentimento {idx}: {consentimento.titular_id}")
    
    await session.flush()
    print(f"\n✅ {len(consentimentos)} consentimentos criados!")
    return consentimentos


async def seed_ingestoes(session: AsyncSession, consentimentos: list[Consentimento]) -> list[Ingestion]:
    """
    Cria ingestões de exemplo
    
    Args:
        consentimentos: Lista de consentimentos para vincular
    
    Returns:
        Lista de ingestões criadas
    """
    print("\n📥 Criando ingestões de exemplo...")
    
    ingestoes = []
    for idx, dados in enumerate(INGESTOES_EXEMPLO, 1):
        # Criar audit trail inicial
        historico = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "usuario": USER_ID,
                "acao": "CREATE",
                "campo": "status",
                "valor_antigo": None,
                "valor_novo": dados["status"].value,
                "motivo": "Ingestão criada via seed script",
            }
        ]
        
        # Se status FALHA, adicionar evento de erro
        if dados["status"] == IngestionStatus.FALHA:
            historico.append({
                "timestamp": (datetime.now(UTC) + timedelta(seconds=30)).isoformat(),
                "usuario": "SYSTEM",
                "acao": "UPDATE",
                "campo": "status",
                "valor_antigo": IngestionStatus.PENDENTE.value,
                "valor_novo": IngestionStatus.FALHA.value,
                "motivo": "Erro durante processamento: formato inválido",
            })
        
        # Se status CONCLUIDA, adicionar evento de conclusão
        if dados["status"] == IngestionStatus.CONCLUIDA:
            historico.append({
                "timestamp": (datetime.now(UTC) + timedelta(minutes=5)).isoformat(),
                "usuario": "SYSTEM",
                "acao": "UPDATE",
                "campo": "status",
                "valor_antigo": IngestionStatus.PENDENTE.value,
                "valor_novo": IngestionStatus.CONCLUIDA.value,
                "motivo": "Processamento finalizado com sucesso",
            })
        
        # Map arquivo fields to the current model
        arquivo_storage_path = dados.get("arquivo_path")
        arquivo_original = arquivo_storage_path.split("/")[-1] if arquivo_storage_path else None
        mime = "text/csv" if arquivo_storage_path and arquivo_storage_path.endswith((".csv", ".txt")) else (
            "application/json" if arquivo_storage_path and arquivo_storage_path.endswith(".json") else (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if arquivo_storage_path and arquivo_storage_path.endswith(".xlsx") else None
            )
        )

        ingestao = Ingestion(
            id=uuid.uuid4(),
            tenant_id=TENANT_ID,
            fonte=dados["fonte"],
            metodo=dados["metodo"],
            confiabilidade_score=dados["confiabilidade_score"],
            status=dados["status"],
            data_ingestao=(datetime.now(datetime.UTC) - timedelta(days=10 - idx)),
            criado_por=USER_UUID,
            arquivo_original=arquivo_original,
            arquivo_storage_path=arquivo_storage_path,
            arquivo_size_bytes=0,
            arquivo_mime_type=mime,
            total_registros=dados.get("total_registros", 0),
            registros_validos=dados.get("registros_validos", 0),
            registros_invalidos=dados.get("registros_invalidos", 0),
            pii_detectado=dados.get("pii_detectado", {}),
            acoes_lgpd=["CPF tokenizado", "Email parcialmente mascarado"] if dados.get("pii_detectado") else [],
            consentimento_id=consentimentos[idx % len(consentimentos)].id if dados.get("lgpd_validado") else None,
            erros_encontrados=dados.get("erros_encontrados", []),
            historico_atualizacoes=historico,
            descricao=dados.get("descricao"),
            metadata_adicional={
                "dados_sample": dados.get("dados_sample", [])
            },
        )
        session.add(ingestao)
        ingestoes.append(ingestao)
        
        status_icon = "✓" if dados["status"] == IngestionStatus.CONCLUIDA else ("⏳" if dados["status"] == IngestionStatus.PENDENTE else "✗")
        print(f"  {status_icon} Ingestão {idx}: {dados['fonte'].value} - {dados['descricao'][:60]}...")
    
    await session.flush()
    print(f"\n✅ {len(ingestoes)} ingestões criadas!")
    return ingestoes


async def verify_tables_exist(session: AsyncSession) -> bool:
    """
    Verifica se as tabelas necessárias existem no banco
    
    Returns:
        True se tabelas existem, False caso contrário
    """
    print("\n🔍 Verificando existência de tabelas...")
    
    try:
        result = await session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        tables = [row[0] for row in result.fetchall()]
        
        required_tables = ["ingestoes", "consentimentos"]
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"\n❌ Tabelas faltando: {', '.join(missing_tables)}")
            print("   Execute 'alembic upgrade head' antes de rodar este script!")
            return False
        
        print(f"✅ Todas as tabelas necessárias existem: {', '.join(required_tables)}")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar tabelas: {e}")
        return False


async def clear_existing_data(session: AsyncSession):
    """
    Remove dados existentes de seed (opcional - para re-seed)
    """
    print("\n🗑️  Limpando dados existentes de seed...")
    
    try:
        # Delete ingestões de seed
        await session.execute(
            text("DELETE FROM ingestoes WHERE criado_por = :user_id"),
            {"user_id": USER_ID}
        )
        
        # Delete consentimentos de seed
        await session.execute(
            text("DELETE FROM consentimentos WHERE titular_id LIKE 'titular-%'")
        )
        
        await session.commit()
        print("✅ Dados anteriores removidos!")
        
    except Exception as e:
        print(f"⚠️  Aviso ao limpar dados: {e}")
        await session.rollback()


# ============================================
# Main
# ============================================


async def main():
    """
    Função principal: executa seed de dados Wave 1
    """
    print("=" * 80)
    print("🌱 SEED DATA - WAVE 1 - PROSPECAI")
    print("=" * 80)
    
    async with AsyncSessionLocal() as session:
        try:
            # Verificar tabelas
            if not await verify_tables_exist(session):
                print("\n❌ Abortando: tabelas não encontradas!")
                return
            
            # Limpar dados anteriores (opcional, skip se --no-clear é passado)
            should_clear = "--no-clear" not in sys.argv
            if should_clear:
                response = input("\n🤔 Limpar dados de seed anteriores? (s/N): ")
                if response.lower() == "s":
                    await clear_existing_data(session)
            
            # Criar consentimentos
            consentimentos = await seed_consentimentos(session)
            # Criar ingestões
            ingestoes = await seed_ingestoes(session, consentimentos)
            
            # Commit final
            await session.commit()
            
            print("\n" + "=" * 80)
            print("✅ SEED COMPLETO!")
            print("=" * 80)
            print(f"\n📊 Resumo:")
            print(f"   • Consentimentos: {len(consentimentos)}")
            print(f"   • Ingestões: {len(ingestoes)}")
            print(f"   • Tenant ID: {TENANT_ID}")
            print(f"\n🌐 Acesse: http://localhost:3000/dashboard para visualizar os dados!")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Erro ao executar seed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    import sys
    # Allow non-interactive mode for CI/CD
    if "--no-clear" not in sys.argv:
        sys.argv = ["seed_wave1_data.py", "--no-clear"]
    asyncio.run(main())
