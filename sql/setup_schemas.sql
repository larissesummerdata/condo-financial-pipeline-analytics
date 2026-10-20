-- =============================================================================
-- PROJETO: PIPELINE ANALYTICS AUDITORIA CONTABIL
-- DESCRIÇÃO: Criação dos Schemas da Arquitetura Medalhão e Tabelas Bronze (RAW)
-- DATA WAREHOUSE: Supabase (PostgreSQL 15+)
-- =============================================================================

-- 1. Criação dos Schemas Isolados
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- =============================================================================
-- CAMADA BRONZE (RAW / INGESTÃO)
-- =============================================================================

-- Tabela 1: Extrato Bancário da Conta Corrente
CREATE TABLE IF NOT EXISTS bronze.raw_extrato_bancario (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_movimentacao TEXT,
    descricao_historico TEXT,
    documento_numero TEXT,
    valor_transacao TEXT,
    tipo_operacao TEXT, -- 'C' (Crédito) ou 'D' (Débito)
    saldo_resultante TEXT,
    ordem_linha_extrato INTEGER,
    pagina_origem INTEGER,
    arquivo_origem TEXT,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela 2: Relatório de Arrecadação e Boletos Pagos
CREATE TABLE IF NOT EXISTS bronze.raw_cobranca_boletos (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    unidade_bloco TEXT,
    competencia TEXT,
    vencimento_original TEXT,
    data_pagamento TEXT,
    valor_taxa_ordinaria TEXT,
    valor_fundo_reserva TEXT,
    valor_outros_acrescimos TEXT,
    valor_total_pago TEXT,
    pagina_origem INTEGER,
    arquivo_origem TEXT,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela 3: Livro Razão Contábil (Apropriação Analítica de Despesas e Receitas)
CREATE TABLE IF NOT EXISTS bronze.raw_razao_despesas (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_conta TEXT,
    classificacao_contabil TEXT,
    data_lancamento TEXT,
    documento_referencia TEXT,
    historico_lancamento TEXT,
    valor_debito TEXT,
    valor_credito TEXT,
    ordem_linha_razao INTEGER,
    pagina_origem INTEGER,
    arquivo_origem TEXT,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- Índices operacionais para agilizar cargas e consultas
CREATE INDEX IF NOT EXISTS idx_raw_extrato_ordem ON bronze.raw_extrato_bancario (ordem_linha_extrato);
CREATE INDEX IF NOT EXISTS idx_raw_boletos_unidade ON bronze.raw_cobranca_boletos (unidade_bloco);
CREATE INDEX IF NOT EXISTS idx_raw_razao_conta ON bronze.raw_razao_despesas (codigo_conta);