# ProspecIA

<div align="center">

![ProspecIA Logo](docs/logo.png)

**Sistema de Prospecção e Gestão de Inovação com IA Responsável**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org)
[![CI](https://github.com/senai/prospecai/workflows/CI%20Pipeline/badge.svg)](https://github.com/senai/prospecai/actions)

</div>

---

## 📋 Sobre o Projeto

ProspecIA é uma plataforma completa para gestão de inovação que integra:

- **Gestão de Fontes de Fomento** - Cadastro e acompanhamento de editais e programas
- **Portfólio Institucional** - Gestão de institutos, projetos e competências
- **CRM de Inovação** - Relacionamento com clientes e gestão de demandas
- **Pipeline de Oportunidades** - Acompanhamento de propostas em kanban
- **IA Responsável** - Sugestões explicáveis com humano sempre no controle
- **Governança LGPD** - Conformidade desde o design

### 🎯 Características Principais

- ✅ Clean Architecture com SOLID principles
- ✅ Multi-tenancy com isolamento por tenant
- ✅ Auditoria completa de todas operações
- ✅ Sugestões IA com explainability
- ✅ Responsive design mobile-first
- ✅ Observabilidade com Prometheus + Grafana
- ✅ 100% Open Source

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web assíncrono
- **PostgreSQL 15** - Banco de dados relacional com RLS/CLS
- **Neo4j** - Banco de grafos para linhagem de dados
- **Apache Kafka** - Mensageria para auditoria
- **MLflow** - Registry de modelos de IA

### Frontend
- **Next.js 14** - Framework React com App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **React Query** - State management e cache

### Infraestrutura
- **Docker** - Containerização
- **Keycloak** - Identidade e RBAC
- **MinIO** - Object storage
- **Prometheus + Grafana** - Monitoramento
- **Loki** - Agregação de logs

---

## 🚀 Quick Start

### Pré-requisitos

- Docker Desktop ou Docker Engine + Docker Compose
- Node.js 18+ (para desenvolvimento frontend local)
- Python 3.11+ (para desenvolvimento backend local)
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/senai/prospecai.git
cd prospecai
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite .env conforme necessário
```

### 3. Inicie todos os serviços

```bash
docker-compose up -d
```

Aguarde alguns minutos para que todos os serviços inicializem completamente.

### 4. Acesse as aplicações

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Keycloak** | http://localhost:8080 | admin / admin |
| **Grafana** | http://localhost:3001 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **MLflow** | http://localhost:5000 | - |
| **Neo4j Browser** | http://localhost:7474 | neo4j / neo4j_password |

---

## 📁 Estrutura do Projeto

```
ProspecIA/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── domain/       # Entidades de negócio
│   │   ├── use_cases/    # Casos de uso
│   │   ├── interfaces/   # Controllers HTTP
│   │   ├── adapters/     # Integrações externas
│   │   └── infrastructure/ # Config, middleware
│   ├── tests/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/             # Next.js frontend
│   ├── app/              # App Router (Next.js 14)
│   ├── components/       # Componentes React
│   ├── lib/              # Utilitários
│   ├── types/            # TypeScript types
│   ├── package.json
│   └── Dockerfile
│
├── docker/               # Configurações Docker
│   ├── keycloak/
│   ├── prometheus/
│   └── grafana/
│
├── scripts/              # Scripts utilitários
│   ├── init-db.sql
│   └── seed_data.json
│
├── docs/                 # Documentação
│   ├── implementation_plan.md
│   └── requirements_v2.md
│
├── .github/              # CI/CD workflows
│   └── workflows/
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 💻 Desenvolvimento Local

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor de desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Rodar servidor de desenvolvimento
npm run dev
```

### Linting e Formatação

```bash
# Backend
cd backend
black .
flake8 .
mypy app/

# Frontend
cd frontend
npm run lint
npm run format
```

---

## 🧪 Testes

### Backend

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend

```bash
cd frontend
npm run test
```

---

## 📊 Monitoramento e Observabilidade

### Métricas (Prometheus)

Acesse http://localhost:9090 para queries diretas ou use o Grafana.

### Dashboards (Grafana)

1. Acesse http://localhost:3001
2. Login: admin / admin
3. Dashboards pré-configurados em "Dashboards > Browse"

### Logs (Loki)

Logs centralizados disponíveis no Grafana via datasource Loki.

---

## 🔐 Segurança

- **Autenticação**: Keycloak com OIDC/OAuth2
- **Autorização**: RBAC com roles (admin, gestor, analista, viewer)
- **Criptografia**: AES-256 para campos sensíveis
- **Auditoria**: Todas operações registradas por 5 anos
- **LGPD**: Agente de classificação e mascaramento automático

---

## 📖 Documentação

- [Plano de Implementação](docs/implementation_plan.md)
- [Requisitos Funcionais e Não-Funcionais](docs/requirements_v2.md)
- [Guia de Contribuição](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## 🗺️ Roadmap

### Wave 0: Fundação (TRL 3-4) ✅ CURRENT
- Infraestrutura base
- FastAPI + Next.js skeletons
- Observabilidade básica

### Wave 1: Ingestão com Governança (TRL 4-5)
- Ingestão de dados
- Agente LGPD
- Auditoria completa

### Wave 2: Domínios Núcleo (TRL 5-6)
- Gestão de fomento
- Portfólio institucional
- CRM de inovação
- Pipeline de oportunidades

### Wave 3: IA Controlada (TRL 6-7)
- Sugestões IA com explainability
- Matching inteligente
- Análises e gargalos
- Chatbot assistente

### Wave 4: Endurecimento SaaS (TRL 7-8)
- Multi-tenancy com RLS
- Segurança completa
- Responsividade total

### Wave 5: Operação Plena (TRL 8-9)
- Governança de modelos
- Fairness e sustentabilidade
- Auditoria de conformidade

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre o processo.

### Princípios de Desenvolvimento

1. **SOLID** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
2. **Clean Architecture** - Separação de camadas e dependências
3. **Clean Code** - Código legível, testável e manutenível
4. **Humano-no-loop** - IA nunca executa sem aprovação humana
5. **Transparência** - Toda decisão IA é explicável

---

## 📜 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👥 Autores

- **Bruno Xavier** - Arquitetura e Desenvolvimento Inicial

---

## 🙏 Agradecimentos

- SENAI - Suporte e infraestrutura
- Comunidade Open Source
- Todos os contribuidores

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/senai/prospecai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/senai/prospecai/discussions)
- **Email**: suporte@prospecai.com.br

---

<div align="center">

**Feito com ❤️ pelo time SENAI**

[Website](https://prospecai.com.br) • [Documentation](https://docs.prospecai.com.br) • [API Reference](https://api.prospecai.com.br/docs)

</div>
