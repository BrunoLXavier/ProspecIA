# Sistema de Prospecção Inteligente de Projetos de P&D (ProspecAI)

**Documento Fonte da Verdade para Implementação**  
Versão atualizada em Janeiro de 2026

---

## Glossário

- **TRL (Technology Readiness Level)**: Nível de maturidade tecnológica, adaptado para software (1-9: de conceitos básicos a operação plena).
- **PLN (Processamento de Linguagem Natural)**: Técnica de IA para análise de texto.
- **LGPD**: Lei Geral de Proteção de Dados (Brasil).
- **Humano-no-loop**: Validação humana obrigatória em processos de IA.
- **Drill-down**: Navegação de dados agregados para detalhes brutos.
- **Matching**: Algoritmo para emparelhar demandas, capacidades e fomento.
- **SaaS**: Software as a Service (arquitetura em nuvem).
- **API**: Interface de Programação de Aplicações.

## Referências a Padrões

- **Engenharia de Requisitos**: ISO/IEC/IEEE 29148
- **Segurança**: ISO 27001
- **Acessibilidade**: WCAG 2.1
- **Ética de IA**: AI Act (UE) e NIST AI Risk Management Framework

## 1. Requisitos Funcionais (RF)

### RF-01 – Ingestão e Orquestração de Dados Multiorigem

- **RF-01.01** Ingerir dados públicos, privados e internos (identificar e importar dados do RAIS, IBGE, INPI, FINEP e BNDES), com suporte a batch e real-time (RF-01.04), metadados obrigatórios (RF-01.02) e reprocessamento histórico (RF-01.03). O sistema deve permitir integração com APIs externas, sugestões de mapeamento via IA (conforme RF-02.05, com exibição transparente de fontes e confiança conforme PT-03), e validação humana obrigatória (conforme PT-02). Cada ingestão de dados deve incluir os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a anexos (ex.: arquivos CSV ou JSON). O modelo de dados deve ser versionado (ex.: histórico de ingestões visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabela "Ingestoes" no banco de dados relacional, com índices em ID e Data de Ingestão para buscas rápidas; campos armazenados em JSONB para flexibilidade em subcampos; validações: triggers para campos obrigatórios e checagem de integridade referencial com tabelas de fontes (RF-02).

  - **RF-01.01.01** ID: Identificador único da ingestão, gerado automaticamente pelo sistema (ex.: UUID ou "ING-2026-001"). Deve ser imutável, usado para integrações internas (ex.: associação a fontes em RF-02 ou portfólio em RF-03). Funcionalidade: Busca rápida por ID e geração de QR code para compartilhamento seguro. Tipo de dado: UUID (36 caracteres, formato padrão RFC 4122); validação: único no sistema, gerado via função UUID v4; exemplo: "123e4567-e89b-12d3-a456-426614174000".

  - **RF-01.01.02** Fonte de Dados: Origem dos dados (ex.: "RAIS", "IBGE", "INPI", "FINEP", "BNDES", ou fontes privadas como bancos internos). Subcampos: Tipo (Pública/Privada/Interna, enum: ['publica', 'privada', 'interna']); URL ou Endpoint (ex.: API URL, string até 500 caracteres, validação regex para URL válida); Credenciais (ex.: chave de API, mascarada para segurança conforme RNF-03.01, string criptografada AES-256). Funcionalidade: IA sugere fontes baseadas em análise de necessidades (ex.: via PLN em descrições de projetos de RF-03.01), com opção de rejeição humana e registro de feedback (PT-05.04). Estrutura: JSON object com subcampos; validação: tipo obrigatório, URL deve ser acessível via HTTP check.

  - **RF-01.01.03** Método de Ingestão: Método utilizado (ex.: "API Pull", "Batch Upload", "Real-time Streaming"). Subcampos: Frequência (ex.: "Diária", "Sob Demanda", enum: ['diaria', 'semanal', 'mensal', 'sob_demanda']); Formato (ex.: JSON, CSV, XML, enum: ['json', 'csv', 'xml', 'outros']). Funcionalidade: Suporte a orquestração automática (ex.: via ferramentas como Apache Airflow), com alertas para falhas (ex.: "Ingestão falhou em 07/01/2026"). IA otimiza métodos baseados em volume de dados, exibindo hipóteses e fontes (PT-03). Estrutura: JSON object; validação: formato deve corresponder a parsers disponíveis no sistema.

  - **RF-01.01.04** Metadados: Informações descritivas obrigatórias. Subcampos: Data de Ingestão (ex.: "07/01/2026 15:00", tipo: timestamp ISO 8601); Confiabilidade (ex.: score de 0-100, tipo: integer, calculado via IA); Método de Validação (ex.: "Checksum", string até 100 caracteres); Tamanho (ex.: "500 MB", tipo: decimal com unidade enum ['KB', 'MB', 'GB']). Funcionalidade: Geração automática de metadados, com validação humana para scores < 80% (PT-02). Estrutura: JSON object; validação: data deve ser futura ou atual, score entre 0-100.

  - **RF-01.01.05** Dados Ingeridos: Conteúdo dos dados (ex.: registros de patentes do INPI ou editais da FINEP). Subcampos: Volume (ex.: "10.000 registros", tipo: integer); Campos Mapeados (ex.: "CNPJ → Cliente ID em RF-04.01", array de strings); Transformações Aplicadas (ex.: normalização de datas, array de objetos {transformacao: string, parametros: json}). Funcionalidade: Mapeamento automático via IA para entidades do sistema (ex.: matching com clientes em RF-04.01), com drill-down para dados brutos (PT-04.01). Alertas para dados desatualizados (ex.: > 30 dias). Estrutura: Blob ou referência a storage (ex.: S3), com metadados em JSON; validação: volume > 0.

  - **RF-01.01.06** Status de Ingestão: Estado atual (ex.: "Pendente", "Concluída", "Falha"). Subcampos: Erros Encontrados (ex.: "Formato inválido em 5% dos registros", array de strings); Ações Corretivas (ex.: "Reprocessar", string). Funcionalidade: Reprocessamento histórico (RF-01.03), com simulação de impactos antes de execução (RF-05.07). Estrutura: Enum ['pendente', 'concluida', 'falha']; validação: transição apenas por usuários autorizados.

  - **RF-01.01.07** Histórico de Atualizações: Registro cronológico de alterações na ingestão. Subcampos: ID da Atualização (ex.: "UPD-001", string única); Data/Hora (ex.: "07/01/2026 15:30", timestamp); Usuário Responsável (ex.: ID do usuário, foreign key); Mudança (ex.: "Reprocessamento executado", string); Motivo (ex.: "Atualização de fonte", obrigatório para auditoria, string não vazia). Funcionalidade: Visualização em timeline interativa com diff visual (PT-01.02). Integração com monitoramento contínuo (RF-02.03). Estrutura: Array de JSON objects; validação: motivo obrigatório se mudança manual.

  - **RF-01.01.08** Busca e Filtros Avançados: Suporte a filtros dinâmicos (ex.: por fonte, data > 2026, método de ingestão, status, ou confiabilidade > 80), com suporte a operadores lógicos (AND/OR), ordenação (ascendente/descendente por campos como data ou volume), e paginação (ex.: 10 itens por página com navegação). Funcionalidade: Busca textual fuzzy em campos como fonte ou metadados, com exportação para CSV/PDF (RF-09.01). Estrutura: Queries otimizadas com índices compostos (ex.: índice em fonte + data para filtros combinados); validação: filtros devem retornar resultados em < 2 segundos para até 1 milhão de registros.

  - **RF-01.01.09** Integrações: Associação automática a clientes (RF-04.06 via matching de CNPJ), portfólio (RF-03.06 via TRL ou setores), e pipeline (RF-05.01 via oportunidades derivadas de dados ingeridos). Suporte a APIs para importação externa (RNF-04.01), incluindo webhooks para notificações real-time de novas ingestões e endpoints RESTful para consulta (ex.: GET /ingestions/{id} retornando JSON com todos os campos). Funcionalidade: Sincronização bidirecional com fontes externas (ex.: pull de dados do INPI via API oficial, push de logs para sistemas de BI). Estrutura: Foreign keys para tabelas relacionadas; validação: autenticação OAuth2 para integrações seguras.

  - **RF-01.01.10** Segurança e Conformidade: Dados sensíveis anonimizados (RNF-03.01). Conformidade LGPD: Consentimento para dados privados.

  - **RF-01.01.11** Usabilidade: Interface mobile-first (RNF-04.05), com sugestões IA em pop-ups editáveis. Testes de acessibilidade conforme WCAG 2.1.

- **RF-01.02** Metadados obrigatórios: fonte, data, método, confiabilidade.

- **RF-01.03** Reprocessamento histórico.

- **RF-01.04** Suporte a batch e real-time.

### RF-02 – Gestão de Fontes de Fomento e Oportunidades

- **RF-02.01** Cadastro gerenciável de fontes de fomento (ex.: agências como FINEP, BNDES, CNPq, ou programas internacionais como Horizon Europe), com suporte a múltiplas instâncias por usuário autorizado. O sistema deve permitir importação automatizada de dados públicos (integração com APIs de fontes oficiais, conforme RF-01.01), sugestões de preenchimento via IA (conforme RF-02.05, com exibição transparente de fontes e confiança conforme PT-03), e validação humana obrigatória (conforme PT-02). Cada registro de fonte de fomento deve incluir os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a anexos (ex.: editais em PDF). O modelo de dados deve ser versionado (ex.: histórico de alterações visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabela "FontesFomento" em banco relacional, com foreign keys para tabelas de setores e TRL; campos em JSONB para listas múltiplas; validações: constraints unique em ID, check para TRL entre 1-9.

  - **RF-02.01.01** ID: Identificador único do registro, gerado automaticamente pelo sistema (ex.: UUID ou número sequencial como "FOM-2026-001"). Deve ser imutável, usado para integrações internas (ex.: associação a oportunidades em RF-05 ou matching em RF-06). Funcionalidade: Busca rápida por ID e geração de QR code para compartilhamento seguro. Tipo de dado: UUID; validação: único, gerado via UUID v4.

  - **RF-02.01.02** Nome: Nome completo ou oficial da fonte de fomento (ex.: "Programa de Subvenção Econômica da FINEP" ou "Fundo Nacional de Desenvolvimento Científico e Tecnológico"). Suporte a busca textual fuzzy (tolerante a erros de digitação) e sugestões de autocompletar via IA (baseadas em dados históricos ou fontes externas, com exibição de confiança > 80% conforme PT-03.05). Validação: Obrigatório, comprimento máximo de 200 caracteres, sem caracteres especiais proibidos (ex.: scripts maliciosos, conforme RNF-03.01). Tipo de dado: String UTF-8; validação: regex para caracteres alfanuméricos e espaços.

  - **RF-02.01.03** Tipo de Instrumento: Classificação do instrumento de fomento, selecionável de uma lista configurável e gerenciável (ex.: "Subvenção Econômica", "Empréstimo Subsidiado", "Edital de Chamada Pública", "Parceria Público-Privada", "Investimento em Equity"). Subcampos: Descrição Breve (ex.: "Financiamento não reembolsável para projetos de inovação", string até 500 caracteres); Categoria (ex.: "Nacional", "Internacional", "Setorial", enum). Funcionalidade: IA sugere tipo baseado em análise de texto do edital (RF-02.05), com opção de rejeição humana e registro de feedback (PT-05.04). Estrutura: JSON object; validação: tipo em enum pré-definido.

  - **RF-02.01.04** Setor-Alvo: Setores econômicos ou tecnológicos priorizados pela fonte (ex.: "Tecnologia da Informação", "Biotecnologia", "Energia Renovável", "Saúde"), selecionáveis de uma taxonomia gerenciável e hierárquica (ex.: baseada em CNAE ou classificações internacionais como ISIC). Subcampos: Lista Múltipla (permitir até 10 setores, array de strings com peso integer 1-10); Exclusões (ex.: setores não elegíveis, como "Armas" para conformidade ética em PT-07, array de strings). Funcionalidade: Matching automático com setores de clientes (RF-04.01) e portfólio institucional (RF-03.01), com drill-down para detalhes (RF-07.04). IA classifica setores via PLN em textos de editais, exibindo hipóteses e fontes (PT-03). Estrutura: Array de JSON objects; validação: máximo 10 itens, pesos positivos.

  - **RF-02.01.05** TRL Mínimo/Máximo: Faixa de níveis de maturidade tecnológica exigidos (escala 1-9, adaptada para software conforme glossário). Subcampos: TRL Mínimo (ex.: 3 – Prova de Conceito, integer 1-9); TRL Máximo (ex.: 7 – Demonstração em Ambiente Operacional, integer 1-9); Descrição da Faixa (ex.: "Projetos em estágio inicial a protótipos funcionais", string). Funcionalidade: Validação automática contra TRL de projetos no portfólio (RF-03.01), com alertas se houver incompatibilidade (ex.: "TRL do projeto X é 2, abaixo do mínimo"). IA sugere ajustes baseados em histórico (RF-02.05), com simulação de cenários (RF-05.07) e validação humana obrigatória. Estrutura: JSON object; validação: mínimo <= máximo, valores em 1-9.

  - **RF-02.01.06** Valor Disponível: Montante financeiro total ou estimado disponível para a fonte (ex.: "R$ 100.000.000,00" ou "US$ 50 milhões"). Subcampos: Moeda (ex.: BRL, USD, EUR, enum com conversão automática via API de câmbio em tempo real); Valor Mínimo por Projeto (ex.: "R$ 500.000,00", decimal >0); Valor Máximo por Projeto (ex.: "R$ 10.000.000,00", decimal >0); Disponibilidade Atual (ex.: percentual restante, integer 0-100, atualizado via monitoramento em RF-02.03). Funcionalidade: Cálculo de compatibilidade financeira com orçamentos de projetos (RF-03.01), com exibição de fórmulas e margens de erro (PT-03.03). Alertas automáticos se o valor disponível cair abaixo de 20% (RF-02.09). Estrutura: JSON object; validação: valores numéricos positivos, moeda em enum.

  - **RF-02.01.07** Prazo de Submissão: Datas limites para submissão de propostas. Subcampos: Data de Abertura (ex.: "01/02/2026", date); Data de Encerramento (ex.: "30/06/2026", date); Prazo de Prorrogação (campo opcional para atualizações, date); Frequência (ex.: "Anual", "Contínuo", "Único", enum). Funcionalidade: Integração com calendário do sistema para alertas personalizáveis (ex.: e-mails 30/15/7 dias antes, conforme RF-02.09). IA monitora e atualiza prazos via scraping de sites oficiais (RF-02.03), com validação humana e registro de rejeições (PT-02.05). Estrutura: JSON object; validação: abertura < encerramento.

  - **RF-02.01.08** Critérios de Elegibilidade: Requisitos para participação, descritos de forma estruturada e gerenciável. Subcampos: Lista de Critérios (ex.: "Empresa com CNPJ ativo", "Parceria com instituto de pesquisa", "Alinhamento com ODS da ONU", array de objetos {criterio: string, tipo: enum ['texto', 'checkbox', 'pontuacao'], valor: any}); Documentos Exigidos (ex.: "Plano de Negócios", "Comprovante de TRL", array de strings com upload de templates reutilizáveis de RF-08.07); Restrições (ex.: "Exclusivo para PMEs", "Regiões específicas: Norte/Nordeste", array de strings); Pontuação Mínima (ex.: "Score de elegibilidade >= 70%", integer 0-100). Funcionalidade: Análise automática de aderência via IA (RF-06.01), com exibição detalhada de scores, hipóteses e fontes (PT-03). Humano pode ajustar critérios e recalcular (RF-06.04), com registro de decisões (RF-06.05). Estrutura: JSON array; validação: pontuação mínima <=100.

  - **RF-02.01.09** Histórico de Atualizações: Registro cronológico de todas as alterações no registro. Subcampos: ID da Atualização (ex.: "UPD-001", string); Data/Hora (ex.: "07/01/2026 14:59", timestamp); Usuário Responsável (ex.: ID do usuário, foreign key com link para perfil); Campo Alterado (ex.: "Valor Disponível", string); Valor Antigo/Novo (ex.: "R$ 100M → R$ 80M", json {antigo: any, novo: any}); Motivo (ex.: "Atualização oficial do edital", campo obrigatório para auditoria, string não vazia); Fonte da Atualização (ex.: "Site da FINEP", string com link e data de acesso, timestamp). Funcionalidade: Visualização em timeline interativa com diff visual (PT-01.02). Integração com monitoramento contínuo (RF-02.03) para atualizações automáticas via IA, com aprovação humana (PT-02). Estrutura: Array de JSON objects; validação: motivo obrigatório.

  - **RF-02.01.10** Busca e Filtros Avançados: Suporte a filtros dinâmicos (ex.: por setor, TRL entre 3-7, prazo < 30 dias, tipo de instrumento, ou valor disponível > R$1M), com operadores lógicos (AND/OR/NOT), ordenação (ex.: por prazo ascendente), e paginação (ex.: 20 itens por página com busca infinita scrolling). Funcionalidade: Busca avançada com autocompletar IA para termos comuns (ex.: setores via PLN), e exportação para CSV/PDF (RF-09.01) com opções de formatação (ex.: incluir/excluir colunas). Estrutura: Queries SQL otimizadas com full-text search; validação: resultados em < 1 segundo para filtros complexos.

  - **RF-02.01.11** Integrações: Associação automática a clientes (RF-04.06 via matching de setores ou demandas), portfólio (RF-03.06 via TRL ou competências), e pipeline (RF-05.01 via oportunidades geradas de fontes monitoradas). Suporte a APIs para importação externa (RNF-04.01), incluindo endpoints para CRUD (ex.: POST /fontes para criar registro via JSON payload) e webhooks para atualizações em tempo real (ex.: notificação de novo edital). Funcionalidade: Integração bidirecional com fontes oficiais (ex.: pull de editais do FINEP, push de associações para sistemas CRM externos). Estrutura: RESTful APIs com autenticação JWT; validação: rate limiting para prevenir abusos.

  - **RF-02.01.12** Segurança e Conformidade: Campos sensíveis (ex.: valores financeiros) mascarados para usuários de baixo privilégio (RNF-03.03). Conformidade LGPD: Consentimento para dados pessoais em critérios de elegibilidade.

  - **RF-02.01.13** Usabilidade: Interface mobile-first (RNF-04.05), com sugestões IA exibidas em pop-ups editáveis. Testes de acessibilidade conforme WCAG 2.1.

- **RF-02.02** Modelagem configurável de instrumentos, critérios e regras.

- **RF-02.03** Monitoramento contínuo de chamadas e oportunidades.

- **RF-02.04** Classificação por tipo, setor, TRL, exigências regulatórias.

- **RF-02.05** IA auxiliar na captura, atualização e classificação (p. ex. Google Gemini).

- **RF-02.06** Associação a clientes, demandas e capacidades.

- **RF-02.07** Exibição completa de sugestões IA (conforme PT-03).

- **RF-02.08** Validação, correção ou rejeição humana.

- **RF-02.09** Alertas automáticos para prazos de submissão (ex.: 30, 15, 7 dias antes).

- **RF-02.10** Priorização de fontes baseada em compatibilidade com portfólio institucional.

### RF-03 – Gestão do Portfólio Institucional

- **RF-03.01** Cadastro versionado de projetos, equipes, infraestrutura e competências, com suporte a modelagem gerenciável (RF-03.02), associação a lições aprendidas (RF-03.03) e sugestões IA para preenchimento (RF-03.04). O sistema deve permitir importação de dados (conforme RF-01.01), exibição transparente de sugestões (RF-03.05) e ajustes humanos (RF-03.06). Cada entidade deve incluir os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a anexos (ex.: relatórios de projetos). O modelo de dados deve ser versionado (ex.: histórico de alterações visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabelas separadas para cada entidade (ex.: "Institutos", "Projetos") com relações many-to-many via tabelas de junção; campos em JSONB para listas; validações: foreign keys e checks para TRL 1-9.

  - **RF-03.01.01** Instituto: Entidade representando a instituição. Subcampos: ID (gerado automaticamente, ex.: "INS-2026-001", UUID); Nome (ex.: "Instituto XYZ", string até 200); Localização (Região/Estado/Cidade, json {regiao: enum, estado: string, cidade: string}); Setores de Atuação (lista múltipla, array de strings); Tipo (Público/Privado, enum); Data de Fundação (ex.: "01/01/2000", date); Contato Principal (ex.: e-mail, string validação regex email); Histórico de Projetos (IDs associados, array de UUIDs); Capacidade de Investimento Estimada (ex.: "R$ 50M", decimal). Funcionalidade: Matching automático com fontes de fomento (RF-02.06), com drill-down para projetos. IA sugere preenchimento baseado em dados ingeridos (RF-01.01), exibindo fontes (PT-03). Validação: nome não vazio, data fundação passada.

  - **RF-03.01.02** Projeto: Entidade para projetos de P&D. Subcampos: ID (ex.: "PROJ-2026-001", UUID); Nome (ex.: "Desenvolvimento de IA", string); Descrição (texto detalhado, string até 5000); Instituto Associado (ID, foreign key); TRL (1-9, ex.: 5, integer); Status (Em Desenvolvimento/Concluído/Cancelado, enum); Data de Início/Fim (ex.: "01/01/2026 - 31/12/2026", json {inicio: date, fim: date}); Orçamento (ex.: "R$ 1M", decimal); Equipe Associada (IDs, array); Infraestrutura Utilizada (IDs, array); Resultados Esperados (ex.: "Protótipo funcional", string); Indicadores de Sucesso (ex.: KPIs, json array). Funcionalidade: Validação TRL contra fontes (RF-02.01), com alertas para incompatibilidades. IA sugere status baseado em histórico, com validação humana (PT-02). Validação: início < fim, TRL 1-9.

  - **RF-03.01.03** Equipe: Entidade para membros da equipe. Subcampos: ID (ex.: "EQP-2026-001", UUID); Nome Completo (ex.: "João Silva", string); Competências Principais (lista de IDs, array); Cargo (ex.: "Pesquisador", string); Projetos Associados (IDs, array); Telefone Interno (string, regex telefone); E-mail Interno (string, regex email); Link do LinkedIn (string, URL); Link do Lattes (string, URL). Funcionalidade: Análise de rede via IA (RF-05.05), com sugestão de alocações. Validação: e-mail único.

  - **RF-03.01.04** Infraestrutura: Entidade para recursos físicos/digitais. Subcampos: ID (ex.: "INF-2026-001", UUID); Nome (ex.: "Laboratório de IA", string); Tipo (Laboratório/Equipamento/Software, enum); Localização (Instituto/Região, json); Capacidade (ex.: "10 usuários", integer); Status (Disponível/Em Manutenção, enum); Projetos Associados (IDs, array); Data de Aquisição (date); Custo de Manutenção Anual (ex.: "R$ 100K", decimal). Funcionalidade: Otimização via IA para alocação em projetos. Validação: capacidade >0.

  - **RF-03.01.05** Lições Aprendidas: Entidade para conhecimentos acumulados. Subcampos: ID (ex.: "LIC-2026-001", UUID); Projeto Associado (ID, foreign key); Descrição do Contexto (string); Problema Enfrentado (string); Solução Adotada (string); Impacto (Positivo/Negativo, enum); Data de Registro (timestamp); Responsável pelo Registro (ID usuário); Categoria (Técnica/Gestão/Financeira, enum); Aplicabilidade a Outros Projetos (Sim/Não, boolean). Funcionalidade: Integração com relatórios estratégicos (RF-09.04). Validação: data registro atual.

  - **RF-03.01.06** Competência Tecnológica: Entidade para habilidades institucionais. Subcampos: ID (ex.: "COMP-2026-001", UUID); Nome (ex.: "Machine Learning", string); Descrição (string); Categoria (ex.: Software, enum); Nível de Maturidade (Baixo/Médio/Alto, enum); Equipes Associadas (IDs, array); Projetos Associados (IDs, array); Data de Avaliação (date); Evidências de Aplicação (ex.: Patentes/Publicações, array de strings). Funcionalidade: Matching com demandas (RF-06.01). Validação: nível em enum.

  - **RF-03.01.07** Busca e Filtros Avançados: Suporte a filtros por entidade (ex.: projetos por TRL >5, equipes por competência), status, data de fundação, ou setores, com operadores lógicos e ordenação (ex.: por nome alfabético). Funcionalidade: Busca global com sugestões IA para termos relacionados (ex.: "IA" sugere projetos com Machine Learning), e exportação seletiva. Estrutura: Índices em campos chave como TRL e nome para queries eficientes; validação: suporte a exportação em formatos múltiplos.

  - **RF-03.01.08** Integrações: Com matching (RF-06.01 via associações automáticas de competências a demandas), ingestão (RF-01.01 para importação de projetos históricos), e pipeline (RF-05.01 para alocação de recursos em oportunidades). Suporte a APIs para sincronização (ex.: GET /projetos para listar com filtros JSON). Funcionalidade: Exportação para ferramentas externas (ex.: integração com Google Sheets para relatórios). Estrutura: Foreign keys e endpoints RESTful; validação: autenticação por role.

  - **RF-03.01.09** Segurança e Conformidade: Controle de acesso (RNF-03.03).

  - **RF-03.01.10** Usabilidade: CRUDs com sugestões IA.

- **RF-03.02** Modelagem gerenciável de dados.

- **RF-03.03** Associação a lições aprendidas.

- **RF-03.04** Agente de IA para sugerir o preenchimento dos CRUDs de cada campo em cada tela.

- **RF-03.05** Exibição transparência de sugestões IA (conforme PT-03) com suas fontes.

- **RF-03.06** Ajuste, complemento ou rejeição humana das sugestões dos agentes de IA para auxílio de preenchimento dos CRUDs.

### RF-04 – CRM de Inovação Integrado e Gestão de Clientes

- **RF-04.01** Cadastro de clientes, decisores e histórico completo de interações, com suporte a registro de demandas (RF-04.02), sugestões IA (RF-04.03) e análise de sentimentos (RF-04.06). O sistema deve permitir consulta à Receita Federal, geração de perfis dinâmicos (RF-04.07) e pontuação de engajamento (RF-04.08), com exibição transparente (RF-04.04) e validação humana (RF-04.05). Cada registro de cliente deve incluir os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a anexos (ex.: atas de reuniões). O modelo de dados deve ser versionado (ex.: histórico de interações visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabela "Clientes" com relações one-to-many para interações e demandas; campos em JSONB para listas; validações: CNPJ único via constraint.

  - **RF-04.01.01** ID: Identificador único do cliente, gerado automaticamente (ex.: UUID ou "CLI-2026-001"). Deve ser imutável, usado para integrações (ex.: associação a oportunidades em RF-05). Funcionalidade: Busca rápida por ID e geração de QR code para compartilhamento seguro. Tipo: UUID.

  - **RF-04.01.02** Nome: Nome completo ou razão social (ex.: "Empresa XYZ Ltda."). Suporte a busca fuzzy. Validação: Obrigatório, máximo 200 caracteres. Funcionalidade: Autocompletar via IA de dados ingeridos (RF-01.01), com confiança > 80% (PT-03.05). Tipo: String.

  - **RF-04.01.03** CNPJ: Número do CNPJ (formato XX.XXX.XXX/XXXX-XX). Funcionalidade: Validação automática via API da Receita Federal, com recuperação de dados (ex.: endereço, situação cadastral). Tipo: String, regex específico para CNPJ.

  - **RF-04.01.04** Consulta Completa à Receita Federal: Funcionalidade automatizada. Subcampos: Razão Social (string); Nome Fantasia (string); Endereço Completo (json); Situação Cadastral (enum); Data de Abertura (date); Atividade Principal (CNAE, string); Atividades Secundárias (array); Capital Social (decimal); Data da Consulta (timestamp); Atualização Periódica (ex.: mensal, enum). Funcionalidade: Atualização automática, com alerta para mudanças. IA sugere atualizações baseadas em monitoramento (RF-02.03). Estrutura: JSON object.

  - **RF-04.01.05** Setor: Área de atuação (ex.: "Tecnologia da Informação"). Subcampos: Lista Pré-definida (personalizável, enum ou array). Funcionalidade: Matching com setores de fomento (RF-02.01).

  - **RF-04.01.06** Contatos da Empresa: Múltiplos contatos. Subcampos por contato: Nome (string); Cargo (string); Email (string, regex); Telefone (array de strings, regex); Data de Cadastro (timestamp). Funcionalidade: Integração com LinkedIn para sugestões (RF-04.03). Estrutura: Array de JSON.

  - **RF-04.01.07** Histórico de Interações: Registro cronológico. Subcampos por interação: ID (UUID); Tipo (enum: Reunião/E-mail/Ligação); Data/Hora (timestamp); Resumo (string); Responsável (ID); Resultado (string); Anexos (array de files). Funcionalidade: Geração de atas automáticas, criação de reuniões no Microsoft Teams com convites automáticos. Análise de sentimentos (RF-04.06). Estrutura: Array de JSON.

  - **RF-04.01.08** Demandas (Explícitas/Implícitas/Latentes): Necessidades do cliente. Subcampos por demanda: ID (UUID); Tipo (enum); Descrição (string); Prioridade (enum: Baixa/Média/Alta); Data (timestamp). Funcionalidade: Sugestão de demandas latentes via IA (RF-04.03). Estrutura: Array de JSON.

  - **RF-04.01.09** Maturidade Estimada: Estágio de prontidão (ex.: "Exploratório"). Subcampos: Base (ex.: interações, string); Data da Última Avaliação (timestamp). Funcionalidade: Sugestão IA com hipóteses (RF-04.04). Tipo: Enum.

  - **RF-04.01.10** Sentimento: Tom emocional (ex.: "Positivo"). Subcampos: Histórico de Variações (array de {data: timestamp, sentimento: enum}); Data da Última Análise (timestamp). Funcionalidade: Análise via PLN em interações. Estrutura: JSON.

  - **RF-04.01.11** Busca e Filtros Avançados: Suporte a filtros por setor, maturidade (ex.: "Exploratório" ou score >70), CNPJ, ou data de interação, com busca fuzzy em nomes e descrições de demandas. Funcionalidade: Filtros combinados (ex.: setor = "Tecnologia" AND sentimento = "Positivo"), ordenação por engajamento, e visualização em lista ou mapa (para localizações). Estrutura: Índices em campos como nome e setor; validação: suporte a exportação filtrada.

  - **RF-04.01.12** Integrações: Com pipeline (RF-05.01 via associação de clientes a oportunidades), ingestão (RF-01.01 para dados de Receita Federal), e matching (RF-06.01 para demandas). Suporte a APIs para sincronização (ex.: POST /clientes para importação em lote). Funcionalidade: Integração com LinkedIn para pull de decisores e notícias. Estrutura: Webhooks para atualizações de interações; validação: conformidade LGPD em trocas de dados.

  - **RF-04.01.13** Segurança e Conformidade: Anonimização de dados (RNF-03.01).

  - **RF-04.01.14** Usabilidade: Perfis dinâmicos interativos.

- **RF-04.02** Registro de demandas explícitas, implícitas e latentes (taxonomias gerenciáveis).

- **RF-04.03** IA sugerir maturidade, investimento, demandas latentes, notícias e decisores (integração LinkedIn).

- **RF-04.04** Explicitação de dados, critérios e hipóteses.

- **RF-04.05** Validação ou personalização humana.

- **RF-04.06** Análise de sentimentos em interações.

- **RF-04.07** Geração de perfis dinâmicos de clientes com dados atualizados.

- **RF-04.08** Sistema de pontuação de engajamento para priorizar abordagens.

### RF-05 – Pipeline Padronizado e Configurável de Oportunidades

- **RF-05.01** Pipeline configurável de prospecção com campos por oportunidade, incluindo suporte a múltiplas instâncias por usuário autorizado, integração com matching (RF-06) e alertas (RF-07.01). O sistema deve permitir customização de estágios, gates e pesos (conforme RF-05.03), com versionamento e auditoria (PT-01). Cada registro de oportunidade deve incluir os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a anexos (ex.: documentos de validação). O modelo de dados deve ser versionado (ex.: histórico de transições de estágio visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabela "Oportunidades" com estado máquina para estágios; JSONB para scores; validações: foreign keys para clientes e fontes.

  - **RF-05.01.01** ID: Identificador único da oportunidade, gerado automaticamente (ex.: UUID ou "OPP-2026-001"). Deve ser imutável, usado para integrações (ex.: associação a clientes em RF-04 ou fontes em RF-02). Funcionalidade: Busca rápida por ID e geração de QR code para compartilhamento seguro. Tipo: UUID.

  - **RF-05.01.02** Estágio Atual: Estágio atual no pipeline (ex.: "Inteligência", "Validação", "Abordagem", "Registro", "Conversão", "Pós-venda"), selecionável de uma lista configurável (conforme RF-05.02). Subcampos: Data de Entrada no Estágio (ex.: "07/01/2026", date); Data de Saída Estimada (date); Gates de Passagem (ex.: critérios de aprovação, json com pontuação mínima integer). Funcionalidade: Transições automáticas sugeridas via IA (RF-05.05), com validação humana obrigatória (PT-02) e registro de rejeições. Estrutura: Enum para estágio; validação: data entrada < saída.

  - **RF-05.01.03** Cliente Associado: Referência ao cliente (ex.: ID de RF-04.01, foreign key, suporte a múltiplos array). Subcampos: Demandas Associadas (ex.: IDs de demandas explícitas/implícitas/latentes, array); Nível de Engajamento (ex.: pontuação de 0-100 de RF-04.08, integer). Funcionalidade: Matching automático com demandas (RF-06.01), com drill-down para histórico de interações (RF-04.01). IA sugere associações baseadas em análise de sentimentos (RF-04.06), exibindo hipóteses e fontes (PT-03).

  - **RF-05.01.04** Fonte de Fomento: Referência à fonte de fomento (ex.: ID de RF-02.01, foreign key, array para múltiplas). Subcampos: Compatibilidade Estimada (ex.: score de 0-100 baseado em TRL e setor, integer); Valor Alocado (ex.: "R$ 5.000.000,00", decimal). Funcionalidade: Validação automática contra critérios de elegibilidade (RF-02.01), com alertas para prazos (RF-02.09). IA prioriza fontes via clustering (RF-05.09), com simulação de cenários (RF-05.07).

  - **RF-05.01.05** Score de Priorização: Pontuação calculada para priorização (ex.: 0-100, baseada em pesos configuráveis de RF-05.03). Subcampos: Componentes do Score (ex.: Viabilidade Técnica: 40%; Financeira: 30%; Estratégica: 30%, json {componente: string, valor: integer}); Fórmula Aplicada (exibição transparente conforme PT-03.03, string). Funcionalidade: Cálculo automático via IA (RF-05.05), com recalculo humano (RF-05.06) e exibição passo a passo.

  - **RF-05.01.06** Data por Estágio: Registro de datas por estágio. Subcampos: Data de Criação (ex.: "01/01/2026", timestamp); Datas de Transição (ex.: "Inteligência: 01/01 a 15/01", array de json {estagio: enum, inicio: date, fim: date}); Data de Encerramento Estimada (date). Funcionalidade: Integração com calendário para alertas preditivos (RF-07.07), com previsão de conversão (RF-05.10).

  - **RF-05.01.07** Responsável: Usuário ou equipe responsável (ex.: ID de usuário ou equipe de RF-03.01, foreign key). Subcampos: Contato (ex.: e-mail, string); Notificações (ex.: preferências para alertas, json). Funcionalidade: Atribuição automática via IA baseada em competências (RF-03.01), com opção de rejeição humana.

  - **RF-05.01.08** Busca e Filtros Avançados: Suporte a filtros dinâmicos (ex.: por estágio, score > 70, região, responsável, ou cliente associado), com operadores lógicos e ordenação (ex.: por score descendente). Funcionalidade: Busca avançada com visualização em kanban filtrado, e exportação para CSV/PDF (RF-09.01) com gráficos embutidos. Estrutura: Índices compostos em estágio + score; validação: suporte a queries personalizadas salvas.

  - **RF-05.01.09** Integrações: Associação automática a portfólio (RF-03.06 via competências), matching (RF-06.01 via scores), e alertas (RF-07.01). Suporte a APIs para integração externa (RNF-04.01), incluindo webhooks para transições de estágio e endpoints para bulk update (ex.: PATCH /oportunidades). Funcionalidade: Sincronização com calendários externos (ex.: Google Calendar para datas). Estrutura: Event-driven architecture para notificações; validação: idempotência em atualizações.

  - **RF-05.01.10** Segurança e Conformidade: Campos sensíveis (ex.: scores financeiros) mascarados (RNF-03.03). Conformidade LGPD: Consentimento para dados de clientes.

  - **RF-05.01.11** Usabilidade: Interface mobile-first (RNF-04.05), com visualização em kanban ou Gantt. Testes de acessibilidade conforme WCAG 2.1.

- **RF-05.02** Pipeline mínimo: Inteligência → Validação → Abordagem → Registro → Conversão → Pós-venda.

- **RF-05.03** Critérios, gates e pesos configuráveis.

- **RF-05.04** Customização regional com rastreabilidade nacional.

- **RF-05.05** IA sugerir priorização, clustering, scoring e análise de redes.

- **RF-05.06** Exibição passo a passo de cálculos.

- **RF-05.07** Simulação de cenários alternativos.

- **RF-05.08** Métricas de desempenho (ex.: taxa de conversão por estágio).

- **RF-05.09** Clustering de oportunidades por setor ou TRL.

- **RF-05.10** Previsão de conversão baseada em dados históricos.

### RF-06 – Matching entre Demandas, Capacidades e Fomento

- **RF-06.01** Análises de aderência em dados estruturados considerando viabilidade técnica, financeira e alinhamento estratégico, com suporte a algoritmos configuráveis (RF-06.02) e exibição detalhada de scores (RF-06.03). O sistema deve permitir ajustes humanos (RF-06.04) e registro de decisões (RF-06.05), com integração a pipeline (RF-05) e relatórios (RF-09). Cada análise de matching deve gerar um registro com os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a simulações (RF-05.07). O modelo de dados deve ser versionado (ex.: histórico de matchings visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabela "Matchings" com graph relations (ex.: Neo4j para visualização); JSONB para scores; validações: scores 0-100.

  - **RF-06.01.01** ID: Identificador único do matching, gerado automaticamente (ex.: "MAT-2026-001"). Deve ser imutável, usado para integrações (ex.: associação a oportunidades em RF-05). Funcionalidade: Busca rápida por ID e visualização gráfica de rede (ex.: graph database conforme PT-04.04). Tipo: UUID.

  - **RF-06.01.02** Demanda Associada: Referência à demanda do cliente (ex.: ID de RF-04.01, foreign key, incluindo tipo: Explícita/Implícita/Latente, enum). Subcampos: Descrição (ex.: "Desenvolvimento de IA para saúde", string); Prioridade (ex.: Alta, enum); Setor (ex.: "Saúde", string). Funcionalidade: Análise automática via PLN (RF-02.05), com sugestão de demandas latentes (RF-04.03).

  - **RF-06.01.03** Capacidade Associada: Referência à capacidade institucional (ex.: ID de projeto ou competência de RF-03.01, foreign key). Subcampos: TRL (ex.: 5, integer); Equipe (ex.: IDs, array); Infraestrutura (ex.: IDs, array). Funcionalidade: Matching com portfólio (RF-03.01), com alertas para gaps (ex.: "TRL insuficiente").

  - **RF-06.01.04** Fomento Associado: Referência à fonte de fomento (ex.: ID de RF-02.01, foreign key). Subcampos: Critérios de Elegibilidade (ex.: score de aderência, integer); Valor Disponível (ex.: "R$ 2.000.000,00", decimal). Funcionalidade: Validação contra prazos e valores (RF-02.01).

  - **RF-06.01.05** Score de Aderência: Pontuação global (ex.: 0-100, integer). Subcampos: Viabilidade Técnica (ex.: 80%, integer baseado em TRL); Financeira (ex.: 70%, integer baseado em orçamentos); Estratégica (ex.: 90%, integer baseado em setores). Funcionalidade: Cálculo via IA com exibição passo a passo (PT-03), recalculo humano (RF-06.04).

  - **RF-06.01.06** Sugestões de Ajustes: Recomendações para melhoria (ex.: "Ajustar TRL para 6" ou "Buscar parceria"). Subcampos: Impacto Estimado (ex.: "+15% no score", integer); Fontes (ex.: dados históricos, array de strings). Funcionalidade: Geração via IA (RF-06.06), com validação humana. Estrutura: Array de JSON.

  - **RF-06.01.07** Busca e Filtros Avançados: Filtros por score > 70, setor, TRL, ou tipo de demanda, com ordenação por score e visualização gráfica de matches. Funcionalidade: Exportação de resultados filtrados para relatórios. Estrutura: Graph queries para redes de matching; validação: filtros em tempo real.

  - **RF-06.01.08** Integrações: Com pipeline (RF-05.01 para scores em oportunidades), dashboards (RF-07.04 para visualizações), e portfólio (RF-03.01 para capacidades). Suporte a APIs para execução de matching (ex.: POST /matchings com payload de IDs). Funcionalidade: Atualizações automáticas via webhooks. Estrutura: Graph database integration; validação: versionamento de algoritmos.

  - **RF-06.01.09** Segurança e Conformidade: Anonimização de dados sensíveis (RNF-03.01).

  - **RF-06.01.10** Usabilidade: Interface com visualizações interativas.

- **RF-06.02** Algoritmos configuráveis e versionados.

- **RF-06.03** Exibição detalhada de scores.

- **RF-06.04** Ajuste de regras e recalculo.

- **RF-06.05** Registro de decisões humanas.

- **RF-06.06** Sugestão de ajustes para melhorar compatibilidade (ex.: ajustar TRL, buscar parcerias).

### RF-07 – Inteligência, Analytics, Dashboards e Assistente

- **RF-07.01** Análises, projeções e alertas automáticos (thresholds configuráveis), com suporte a thresholds personalizáveis e integração com dashboards (RF-07.04). O sistema deve permitir recalculo (RF-07.03) e exibição transparente (PT-03), com foco em gargalos preditivos (RF-07.07). Cada análise deve gerar um registro com os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a simulações. O modelo de dados deve ser versionado (ex.: histórico de análises visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabela "Analises" com JSONB para projeções; validações: thresholds numéricos.

  - **RF-07.01.01** ID: Identificador único da análise (ex.: "ANA-2026-001"). Funcionalidade: Busca rápida e integração com chatbot (RF-07.05). Tipo: UUID.

  - **RF-07.01.02** Tipo de Análise: Categoria (ex.: "Projeção de Conversão", "Análise de Gargalos"). Subcampos: Thresholds (ex.: "Alerta se taxa < 20%", json {valor: integer, condicao: enum}); Período (ex.: "Q1 2026", string). Funcionalidade: Geração automática via IA, com exposição de método (RF-07.02).

  - **RF-07.01.03** Dados de Entrada: Fontes usadas (ex.: IDs de pipeline RF-05.01, array de UUIDs). Subcampos: Margens de Erro (ex.: ±5%, decimal); Confiança (ex.: 90% conforme PT-03.05, integer).

  - **RF-07.01.04** Projeções: Resultados previstos (ex.: "Taxa de conversão: 35%", decimal). Subcampos: Cenários Alternativos (ex.: "Otimista: 45%", json array). Funcionalidade: Simulação (RF-07.03).

  - **RF-07.01.05** Alertas: Notificações geradas (ex.: "Gargalo em Validação", string). Subcampos: Destinatários (ex.: IDs de responsáveis, array); Prioridade (Alta/Média, enum). Funcionalidade: Envio via e-mail ou app, com registro humano (RF-07.06).

  - **RF-07.01.06** Busca e Filtros Avançados: Filtros por tipo de análise, período, ou confiança >80, com ordenação por data. Funcionalidade: Drill-down em projeções para dados de entrada. Estrutura: Índices em tipo e período.

  - **RF-07.01.07** Integrações: Com matching (RF-06.01 para scores), relatórios (RF-09.01 para exportação), e chatbot (RF-07.05 para queries naturais). Suporte a APIs para triggering de análises. Funcionalidade: Integração com BI tools para dashboards dinâmicos. Estrutura: Event-based triggers.

  - **RF-07.01.08** Segurança e Conformidade: Proteção de dados (RNF-03).

  - **RF-07.01.09** Usabilidade: Dashboards interativos.

- **RF-07.02** Exposição de método, dados e margens de erro.

- **RF-07.03** Recalculo e comparação de cenários.

- **RF-07.04** Dashboards configuráveis com drill-down, incluindo métricas por estágio do pipeline (tempo médio, taxa de conversão por responsável).

- **RF-07.05** Chatbot interno explicável.

- **RF-07.06** Registro de interpretações humanas.

- **RF-07.07** Alertas preditivos para gargalos no pipeline.

### RF-08 – Gestão de Propostas e Conhecimento Institucional

- **RF-08.01** Repositório versionado de propostas e documentos, com suporte a colaboração em tempo real (RF-08.06) e templates reutilizáveis (RF-08.07). O sistema deve permitir apoio IA na redação (RF-08.02) e identificação de conteúdo gerado por IA (RF-08.03), com edição humana obrigatória (RF-08.04). Cada item no repositório deve incluir os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a anexos. O modelo de dados deve ser versionado (ex.: histórico de edições visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03), e exportável para relatórios (RF-09). Estrutura de dados: Tabela "Documentos" com versionamento (ex.: Git-like branches); JSONB para conteúdo; validações: status enum.

  - **RF-08.01.01** ID: Identificador único do documento (ex.: "PROP-2026-001"). Funcionalidade: Busca rápida e versionamento Git-like. Tipo: UUID.

  - **RF-08.01.02** Tipo de Documento: Categoria (ex.: "Proposta", "Relatório Técnico"). Subcampos: Status (ex.: "Rascunho", "Finalizado", enum); Data de Criação/Última Edição (json {criacao: timestamp, edicao: timestamp}).

  - **RF-08.01.03** Conteúdo: Texto ou arquivos (ex.: PDF, DOCX). Subcampos: Seções (ex.: "Introdução", "Orçamento", array de {secao: string, texto: string}); Marcação IA (ex.: "Gerado por IA: 30%", integer). Funcionalidade: Apoio PLN para aderência (RF-08.02), com pontuação (RF-08.08). Estrutura: Blob ou string.

  - **RF-08.01.04** Associações: Referências (ex.: ID de oportunidade RF-05.01, foreign key; edital RF-02.01, foreign key). Subcampos: Colaboradores (ex.: IDs de usuários, array). Funcionalidade: Colaboração real-time.

  - **RF-08.01.05** Histórico de Versões: Registro de mudanças. Subcampos: Versão (ex.: 1.2, string); Editor (ex.: ID, foreign key); Motivo (ex.: "Ajuste por feedback", string). Funcionalidade: Diff visual (PT-01.02).

  - **RF-08.01.06** Busca e Filtros Avançados: Filtros por tipo, status, data de edição, ou associações (ex.: documentos por oportunidade). Funcionalidade: Busca em conteúdo com destaque de termos. Estrutura: Full-text search em seções.

  - **RF-08.01.07** Integrações: Com pipeline (RF-05.01 para anexos em oportunidades) e templates (RF-08.07 para pré-preenchimento). Suporte a APIs para upload colaborativo. Funcionalidade: Integração com editores externos (ex.: Google Docs). Estrutura: WebSocket para real-time.

  - **RF-08.01.08** Segurança e Conformidade: Controle de acesso (RNF-03.03).

  - **RF-08.01.09** Usabilidade: Editor colaborativo.

- **RF-08.02** IA apoiar redação, consolidação, aderência e PLN.

- **RF-08.03** Identificação explícita de conteúdo gerado por IA.

- **RF-08.04** Edição humana completa antes de submissão.

- **RF-08.05** Registro de decisões editoriais.

- **RF-08.06** Colaboração em tempo real.

- **RF-08.07** Templates reutilizáveis para propostas com campos pré-preenchidos.

- **RF-08.08** Pontuação de aderência ao edital antes da submissão.

### RF-09 – Relatórios e Exportação

- **RF-09.01** Relatórios personalizáveis (PDF/CSV) com filtros dinâmicos (período, região, setor), incluindo integração com ferramentas de BI (RF-09.02) e exportação visual (RF-09.06). O sistema deve suportar relatórios operacionais (RF-09.03), estratégicos (RF-09.04) e de IA (RF-09.05). Cada relatório deve incluir os seguintes campos detalhados, com validações em tempo real, campos obrigatórios marcados com (*), e suporte a customização. O modelo de dados deve ser versionado (ex.: histórico de relatórios visível em uma timeline), auditável (logs com timestamp, usuário e motivo da mudança, retenção mínima de 5 anos conforme PT-01.03). Estrutura de dados: Tabela "Relatorios" com JSONB para conteúdo; validações: formato enum.

  - **RF-09.01.01** ID: Identificador único do relatório (ex.: "REL-2026-001"). Funcionalidade: Geração automática e agendamento. Tipo: UUID.

  - **RF-09.01.02** Tipo de Relatório: Categoria (ex.: "Operacional", "Estratégico", enum). Subcampos: Filtros Aplicados (ex.: "Período: 2026", json); Formato (PDF/CSV/PNG, enum).

  - **RF-09.01.03** Conteúdo: Dados gerados (ex.: tabelas, gráficos, json). Subcampos: Métricas (ex.: "Taxa de Conversão: 35%", json array); Fontes (ex.: IDs de dados de RF-01, array). Funcionalidade: Drill-down (RF-07.04), com transparência (PT-03).

  - **RF-09.01.04** Parâmetros de Customização: Configurações (ex.: colunas selecionadas, json). Subcampos: Usuário Gerador (ex.: ID, foreign key); Data de Geração (timestamp).

  - **RF-09.01.05** Busca e Filtros Avançados: Filtros por tipo, data de geração, ou usuário, com pré-visualização filtrada. Funcionalidade: Busca em métricas para relatórios semelhantes.

  - **RF-09.01.06** Integrações: Com dashboards (RF-07.04 para dados em tempo real) e BI tools (RF-09.02). Suporte a APIs para geração programática. Funcionalidade: Exportação para Power BI.

  - **RF-09.01.07** Segurança e Conformidade: Mascaramento de dados sensíveis.

  - **RF-09.01.08** Usabilidade: Pré-visualização interativa.

- **RF-09.02** Integração com ferramentas de BI (ex.: Power BI).

- **RF-09.03** Relatórios Operacionais: Oportunidades por Estágio, Tempo Médio por Estágio, Taxa de Conversão, Desempenho por Responsável.

- **RF-09.04** Relatórios Estratégicos: Sucesso por Fonte de Fomento, Compatibilidade de Portfólio, Distribuição por TRL, Impacto de Lições Aprendidas.

- **RF-09.05** Relatórios de IA: Taxa de Rejeição de Sugestões, Precisão de Matching, Feedback Humano.

- **RF-09.06** Exportação visual de gráficos (ex.: PNG).

## 2. Requisitos Não Funcionais (RNF)

### RNF-01 – Escalabilidade, Arquitetura e Manutenibilidade

- **RNF-01.01** Operação simultânea multi-instituto/região/setor.
- **RNF-01.02** Arquitetura SaaS modular (microservices) com isolamento lógico.
- **RNF-01.03** Evolução de regras sem alteração de código.
- **RNF-01.04** Testes e validação de novos agentes/modelos.

### RNF-02 – Governança de IA e Dados

- **RNF-02.01** Humano-no-loop em todos os fluxos IA.
- **RNF-02.02** Explicabilidade técnica e funcional.
- **RNF-02.03** Desligamento seletivo e substituição de modelos.

### RNF-03 – Segurança, Privacidade e LGPD

- **RNF-03.01** Proteção, classificação, mascaramento/anonymização.
- **RNF-03.02** Trilhas de auditoria completas.
- **RNF-03.03** Controle de acesso por papel.
- **RNF-03.04** Conformidade LGPD/GDPR.

### RNF-04 – Interoperabilidade e Usabilidade

- **RNF-04.01** APIs para integração externa.
- **RNF-04.02** Exportação estruturada.
- **RNF-04.03** Interfaces alinhadas ao fluxo real (baixa carga cognitiva).
- **RNF-04.04** Mobile-first design.
- **RNF-04.05** Adaptação automática de layout, tipografia, espaçamento e elementos interativos a diferentes tamanhos de tela (ex.: breakpoints para smartphones, tablets e desktops).
- **RNF-04.06** Testes em navegadores principais (Chrome, Firefox, Safari, Edge) com cobertura mínima de 95% nos testes de responsividade (ex.: usando Lighthouse ou BrowserStack).

### RNF-05 – Internacionalização

- **RNF-05.01** Suporte a múltiplos idiomas (PT-BR, EN).
- **RNF-05.02** Suporte a fusos horários.

## 3. Princípios Transversais Obrigatórios (PT)

Aplicáveis a todos os requisitos funcionais e não funcionais. Incluem métricas mensuráveis onde aplicável.

### PT-01 – Gestão Integral de Dados (Princípio “No Hardcode”)

- **PT-01.01** Configurável via sistema (ex.: interface de admin com validação em tempo real).
- **PT-01.02** Versionado (ex.: histórico de mudanças com diff visual).
- **PT-01.03** Auditável (ex.: logs com timestamp e usuário, retenção mínima de 5 anos).

### PT-02 – IA como Suporte, Nunca como Autoridade Final

- **PT-02.01** Operar apenas em modo recomendação.
- **PT-02.02** Permitir validação humana explícita (ex.: botão de aprovação obrigatório).
- **PT-02.03** Ser editável, ajustável ou rejeitável pelo usuário.
- **PT-02.04** Nenhuma decisão estratégica executada, enviada ou registrada sem validação humana.
- **PT-02.05** Registrar logs de rejeições humanas (meta: taxa de rejeição < 20% para refinamento).

### PT-03 – Transparência Racional, Explicabilidade e Rastreabilidade

- **PT-03.01** Fontes de dados utilizadas (nível "dados").
- **PT-03.02** Transformações passo a passo (nível "informação").
- **PT-03.03** Modelos, regras, fórmulas, versão e parâmetros aplicados.
- **PT-03.04** Inferência ou recomendação final (nível "conhecimento").
- **PT-03.05** Nível de incerteza/confiança (ex.: % ou baixa/média/alta).
- **PT-03.06** Hipóteses assumidas e data de cada dado.

### PT-04 – Cadeia Dado → Informação → Conhecimento

- **PT-04.01** Dados brutos.
- **PT-04.02** Informações processadas.
- **PT-04.03** Conhecimento inferido ou recomendado.
- **PT-04.04** Rastreabilidade completa (ex.: visualização gráfica via graph database).

### PT-05 – Personalização Humana Obrigatória e Aprendizado Supervisionado

- **PT-05.01** Ajustar pesos, critérios ou parâmetros.
- **PT-05.02** Editar, complementar ou rejeitar sugestões.
- **PT-05.03** Simular ou configurar cenários alternativos.
- **PT-05.04** Registrar intervenções e aprender via feedback supervisionado (atualização trimestral de modelos).

### PT-06 – Governança Nacional com Autonomia Regional

- **PT-06.01** Metodologia e regras padronizadas nacionalmente.
- **PT-06.02** Parâmetros ajustáveis regionalmente sem perda de rastreabilidade (ex.: prioridades locais por setor estratégico).
- **PT-06.03** Conflitos resolvidos por regras explícitas e registradas (ex.: score ponderado).
- **PT-06.04** Relatórios específicos para cada unidade regional.

### PT-07 – Sustentabilidade e Ética de IA

- **PT-07.01** Avaliar impactos éticos (ex.: fairness index > 0.8).
- **PT-07.02** Auditoria periódica anual de conformidade (AI Act/NIST).
- **PT-07.03** Minimizar impacto ambiental (ex.: < 1kg CO₂ por 1000 queries).
- **PT-07.04** Relatório de impacto ético e ambiental (ex.: fairness index por matching, emissões por processamento).