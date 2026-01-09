-- ProspecIA Database Initialization Script
-- Creates initial schema and seed data for development/testing

-- ============================================
-- Enable necessary extensions
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy search

-- ============================================
-- Feature Flags Table
-- ============================================
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT false,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default feature flags
INSERT INTO feature_flags (key, enabled, description) VALUES
('ai_suggestions', true, 'Enable AI-powered suggestions'),
('jwt_required', false, 'Require JWT authentication'),
('rls_enabled', false, 'Enable Row-Level Security'),
('audit_logging', true, 'Enable audit logging'),
('lgpd_agent', true, 'Enable LGPD compliance agent');

-- ============================================
-- System Configuration Table
-- ============================================
CREATE TABLE IF NOT EXISTS configuracoes_sistema (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chave VARCHAR(100) UNIQUE NOT NULL,
    valor JSONB NOT NULL,
    versao INTEGER DEFAULT 1,
    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_responsavel VARCHAR(255),
    motivo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default configurations
INSERT INTO configuracoes_sistema (chave, valor, usuario_responsavel, motivo) VALUES
('estagios_pipeline', '["Inteligência", "Validação", "Abordagem", "Registro", "Conversão", "Pós-venda"]', 'system', 'Configuração inicial'),
('setores_validos', '["TI", "Saúde", "Energia", "Agricultura", "Manufatura", "Educação"]', 'system', 'Configuração inicial'),
('trl_minimo', '1', 'system', 'Configuração inicial'),
('trl_maximo', '9', 'system', 'Configuração inicial');

-- ============================================
-- Audit Log Table
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    usuario_id VARCHAR(255),
    acao VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, READ
    tabela VARCHAR(100) NOT NULL,
    record_id VARCHAR(255),
    valor_antigo JSONB,
    valor_novo JSONB,
    ip_cliente VARCHAR(45),
    user_agent TEXT,
    tenant_id VARCHAR(100) DEFAULT 'nacional'
);

-- Indexes for audit_logs
CREATE INDEX IF NOT EXISTS idx_audit_usuario ON audit_logs (usuario_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs (timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_tabela ON audit_logs (tabela);

-- ============================================
-- Tenants Table (Multi-tenancy)
-- ============================================
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    regiao VARCHAR(100),
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default tenant
INSERT INTO tenants (codigo, nome, regiao) VALUES
('nacional', 'Nacional', 'Brasil'),
('sp', 'São Paulo', 'Sudeste'),
('ba', 'Bahia', 'Nordeste');

-- ============================================
-- MLflow Database (for model registry)
-- ============================================
CREATE DATABASE mlflow;

-- ============================================
-- Indexes for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags(key);
CREATE INDEX IF NOT EXISTS idx_config_chave ON configuracoes_sistema(chave);

-- ============================================
-- Comments
-- ============================================
COMMENT ON TABLE feature_flags IS 'Feature flags for dynamic feature toggling';
COMMENT ON TABLE configuracoes_sistema IS 'System configuration with versioning';
COMMENT ON TABLE audit_logs IS 'Audit trail for all system operations';
COMMENT ON TABLE tenants IS 'Multi-tenant configuration';
