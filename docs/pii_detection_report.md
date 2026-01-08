# Relatório de Detecção Expandida de PII

## Resumo das Alterações Implementadas

### 1. Tipos de PII Expandidos

A detecção de Personally Identifiable Information (PII) foi expandida para incluir os seguintes tipos:

#### Documentos Brasileiros:
- **CPF** - Cadastro de Pessoas Físicas (formato: XXX.XXX.XXX-XX)
- **CNPJ** - Cadastro Nacional de Pessoa Jurídica
- **RG** - Registro Geral (formato: X.XXX.XXX-X)
- **PIS/PASEP** - Programa de Integração Social (formato: XXX.XXXXX.XX-X)

#### Dados Pessoais:
- **Nome** - Detectado via NER (Named Entity Recognition) com BERTimbau
- **E-mail** - Endereços eletrônicos (padrão regex)
- **Telefone** - Números de telefone brasileiros (com/sem DDI)
- **Data de Nascimento** - Datas no formato DD/MM/YYYY ou DD-MM-YYYY
- **Endereço** - Endereços brasileiros com padrão genérico

#### Dados Sensíveis:
- **Biometria** - Referências a impressões digitais e dados biométricos
- **Localização** - Localidades detectadas via NER
- **Organização** - Nomes de organizações detectadas via NER

### 2. Relatórios com Informações Explícitas

Os endpoints de relatório LGPD foram melhorados para ser explícitos quando nenhuma detecção for encontrada:

#### GET `/ingestions/{id}/lgpd-report`

**Resposta incluirá:**
- **pii_types_detected**: Contagem de cada tipo de PII encontrado
- **pii_details**: Lista completa com campo `"detected": true/false`
  - Se `detected: true` - inclui contagem e exemplos mascarados
  - Se `detected: false` - deixa explícito que foi verificado mas não encontrado
- **total_pii_instances**: Número total de instâncias PII
- **data_analysis**: Texto descritivo que menciona:
  - Se nenhuma PII foi encontrada (novo)
  - Tipos detectados vs tipos verificados mas não encontrados (novo)
  - Status de consentimento
  - Score de conformidade e nível de risco

**Exemplo de data_analysis quando sem PII:**
```
"Nenhuma instância de dados pessoais foi detectada nesta ingestão. Os seguintes tipos de PII foram verificados: cpf, cnpj, rg, pis, email, phone, birthdate, address, biometric, person, location, organization. Nenhum deles foi encontrado no conteúdo analisado."
```

**Exemplo com PII encontrada:**
```
"A ingestão contém 15 instâncias de dados pessoais distribuídas em 3 tipos diferentes. Tipos detectados: cpf, email, person. Tipos verificados mas não detectados: cnpj, rg, pis, phone, birthdate, address, biometric, location, organization."
```

#### GET `/ingestions/{id}/pii`

**Resposta incluirá:**
- **tipos_verificados**: Total de tipos de PII verificados (12)
- **tipos_detectados**: Quantos tipos foram encontrados
- **tipos_nao_detectados**: Quantos tipos foram verificados mas não encontrados
- **pii_tipos_detectados**: Array com nomes dos tipos encontrados
- **pii_tipos_nao_detectados**: Array com nomes dos tipos não encontrados
- **detalhes**: Lista completa com campo `"detectado": true/false`
  - Cada item inclui: campo, tipo_pii, ocorrências, exemplos_mascarados, nivel_sensibilidade, detectado

### 3. Níveis de Sensibilidade

Cada tipo de PII possui um nível de sensibilidade:

- **ALTO**: CPF, CNPJ, RG, PIS, Data de Nascimento, Biometria
- **MÉDIO**: Localização, Organização
- **BAIXO**: Nome, E-mail, Telefone, Endereço

### 4. Padrões de Regex Implementados

```python
# Documentos
self.cpf_pattern = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'
self.cnpj_pattern = r'\b\d{2}\.?\d{3}\.?\d{3}/?0001-?\d{2}\b'
self.rg_pattern = r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X]\b'
self.pis_pattern = r'\b\d{3}\.?\d{5}\.?\d{2}-?\d{1}\b'

# Contato
self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
self.phone_pattern = r'\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b'

# Data
self.birthdate_pattern = r'\b(?:0[1-9]|[12]\d|3[01])[-/](?:0[1-9]|1[0-2])[-/](?:19|20)\d{2}\b'

# Localização
self.address_pattern = r'\b(?:Rua|Avenida|Av\.|Travessa|Trav\.|Praça|Pça\.)\s+[A-Za-záéíóúãõç\s]+,?\s*\d+(?:\s*[-,]\s*(?:Apto|Apt\.|Bloco|Blco\.)\s*\d+)?'

# Biometria
self.biometric_pattern = r'(?:impressão|impressão digital|biometria|digital|fingerprint)[\s:]*[\w\d]+'
```

### 5. Benefícios da Implementação

✅ **Cobertura Completa**: 12 tipos diferentes de PII em detecção
✅ **Transparência**: Explícito sobre o que foi verificado e o que não foi encontrado
✅ **Conformidade LGPD**: Relatórios mais completos para auditoria
✅ **Acionabilidade**: Recomendações baseadas em tipos específicos de PII
✅ **Níveis de Sensibilidade**: Avaliação de risco apropriada para cada tipo

### 6. Endpoints Atualizados

- `GET /ingestions/{id}/lgpd-report` - Relatório LGPD completo
- `GET /ingestions/{id}/pii` - Detalhes de PII com tipos não detectados explícitos

### 7. Swagger (http://localhost:8000/docs)

Todos os endpoints estão documentados em inglês com:
- Tags em inglês: "Ingestion", "Consent"
- Descrições em inglês
- Exemplos de resposta com o novo campo "detected"

## Testes Recomendados

1. Enviar arquivo com múltiplos tipos de PII
2. Enviar arquivo sem PII (verificar se lista tipos não encontrados)
3. Verificar endpoint `/pii` para ver lista completa de tipos
4. Conferir relatório LGPD com análise detalhada
