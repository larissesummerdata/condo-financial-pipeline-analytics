-- =============================================================================
-- PROJETO: PIPELINE ANALYTICS AUDITORIA CONTABIL
-- DESCRIÇÃO: Criação dos Schemas da Arquitetura Medalhão e Tabelas Bronze (RAW)
-- DATA WAREHOUSE: Supabase (PostgreSQL 15+)
-- =============================================================================


-- 1. Criação dos Schemas da Arquitetura Medalhão
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- =============================================================================
-- TABELA 0: Metadados e Controle de Ingestão de Arquivos (Ingestion Audit Log)
-- =============================================================================
CREATE TABLE bronze.raw_arquivos_controle (
    id_arquivo BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome_arquivo TEXT UNIQUE NOT NULL,
    competencia_declarada TEXT,       -- Ex: '07/2026'
    hash_md5 TEXT UNIQUE,              -- Garante idempotência física
    total_paginas INTEGER,
    status_processamento TEXT DEFAULT 'PROCESSANDO', -- 'CONCLUIDO', 'ERRO'
    processado_em TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TABELA 1: Extrato Bancário Analítico (Caixa Econômica e Aplicações)
-- =============================================================================
CREATE TABLE bronze.raw_extrato_bancario (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arquivo_origem TEXT REFERENCES bronze.raw_arquivos_controle(nome_arquivo) ON DELETE CASCADE,
    numero_pagina INTEGER,
    ordem_linha INTEGER,
    banco_identificador TEXT,         -- Ex: 'CAIXA_57836-0'
    data_movimentacao TEXT,
    numero_documento TEXT,
    descricao_historico TEXT,
    tipo_operacao TEXT,               -- 'C' (Crédito) ou 'D' (Débito)
    valor_transacao TEXT,
    saldo_resultante TEXT,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TABELA 2: Quadro de Destinações e Rubricas Orçamentárias da Cobrança
-- =============================================================================
CREATE TABLE bronze.raw_cobranca_destinacoes (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arquivo_origem TEXT REFERENCES bronze.raw_arquivos_controle(nome_arquivo) ON DELETE CASCADE,
    numero_pagina INTEGER,
    competencia TEXT,
    taxa_rubrica TEXT,                -- 'Taxa de Condomínio', 'Taxa Extra', etc.
    valor_total_declarado TEXT,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TABELA 3: Cobrança e Boletos do Mês (Alinhada estritamente com o relatório)
-- =============================================================================
CREATE TABLE bronze.raw_cobranca_boletos (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arquivo_origem TEXT REFERENCES bronze.raw_arquivos_controle(nome_arquivo) ON DELETE CASCADE,
    numero_pagina INTEGER,
    unidade_bloco TEXT,
    numero_documento TEXT,            -- Número do boleto / Nosso Número
    competencia TEXT,
    destinacao TEXT,                  -- 'Inquilino' ou 'Proprietário'
    data_vencimento TEXT,
    data_pagamento TEXT,
    valor_principal TEXT,
    valor_multa TEXT,
    valor_juros TEXT,
    valor_desconto TEXT,
    valor_total_pago TEXT,
    situacao_cobranca TEXT,           -- 'Pago', 'Negociado', 'Vencido'
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TABELA 4: Livro Razão Contábil Analítico
-- =============================================================================
CREATE TABLE bronze.raw_razao (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arquivo_origem TEXT REFERENCES bronze.raw_arquivos_controle(nome_arquivo) ON DELETE CASCADE,
    numero_pagina INTEGER,
    ordem_linha INTEGER,
    codigo_conta TEXT,                -- Ex: '2.1.01.002'
    classificacao_contabil TEXT,      -- Ex: 'MANUTENÇÃO PREDIAL'
    grupo_contabil TEXT,              -- 'DESPESA COM PESSOAL', 'AQUISIÇÕES', etc.
    data_lancamento TEXT,
    documento_fiscal_ref TEXT,        -- NF, Recibo ou Contrato
    fornecedor_favorecido TEXT,
    historico_detalhado TEXT,
    valor_debito TEXT,
    valor_credito TEXT,
    saldo_atual TEXT,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TABELA 5: Comprovantes, Notas Fiscais e Anexos (Triangulação de Liquidação)
-- =============================================================================
CREATE TABLE bronze.raw_comprovantes (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arquivo_origem TEXT REFERENCES bronze.raw_arquivos_controle(nome_arquivo) ON DELETE CASCADE,
    numero_pagina INTEGER,
    tipo_documento TEXT,              -- 'NOTA_FISCAL', 'PIX', 'TEV', 'BOLETO_PAGO'
    codigo_barras_ou_chave TEXT,      -- Linha digitável ou chave de 44 dígitos NFe
    autenticacao_mecanica TEXT,       -- Autenticação bancária
    favorecido_nome TEXT,
    favorecido_cnpj_cpf TEXT,
    valor_documento TEXT,
    data_liquidacao TEXT,
    contem_imagem_comprovante BOOLEAN DEFAULT FALSE,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- TABELA 6: Relação de Inadimplência e Devedores Acumulados (Inadimplômetro)
-- =============================================================================
CREATE TABLE bronze.raw_inadimplencia (
    id_registro BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    arquivo_origem TEXT REFERENCES bronze.raw_arquivos_controle(nome_arquivo) ON DELETE CASCADE,
    numero_pagina INTEGER,
    competencia_posicao TEXT,         -- Foto da competência (ex: '07/2026')
    unidade_bloco TEXT,
    competencia_devida TEXT,          -- Mês do boleto em atraso
    numero_cota_ou_acordo TEXT,
    data_vencimento_original TEXT,
    valor_principal_original TEXT,
    valor_multa TEXT,
    valor_juros TEXT,
    valor_correcao_monetaria TEXT,
    custas_honorarios TEXT,
    valor_total_devido TEXT,
    status_cobranca TEXT,
    carregado_em TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- ÍNDICES DE PERFORMANCE E AUDITORIA FORENSE
-- =============================================================================
CREATE INDEX idx_extrato_arquivo ON bronze.raw_extrato_bancario (arquivo_origem);
CREATE INDEX idx_extrato_doc ON bronze.raw_extrato_bancario (numero_documento);

CREATE INDEX idx_destinacoes_arquivo ON bronze.raw_cobranca_destinacoes (arquivo_origem);
CREATE INDEX idx_destinacoes_comp ON bronze.raw_cobranca_destinacoes (competencia);

CREATE INDEX idx_cobranca_arquivo ON bronze.raw_cobranca_boletos (arquivo_origem);
CREATE INDEX idx_cobranca_unidade ON bronze.raw_cobranca_boletos (unidade_bloco);
CREATE INDEX idx_cobranca_doc ON bronze.raw_cobranca_boletos (numero_documento);

CREATE INDEX idx_razao_arquivo ON bronze.raw_razao (arquivo_origem);
CREATE INDEX idx_razao_conta ON bronze.raw_razao (codigo_conta);
CREATE INDEX idx_razao_doc ON bronze.raw_razao (documento_fiscal_ref);

CREATE INDEX idx_comprovantes_arquivo ON bronze.raw_comprovantes (arquivo_origem);
CREATE INDEX idx_comprovantes_auth ON bronze.raw_comprovantes (autenticacao_mecanica);

CREATE INDEX idx_inadimplencia_arquivo ON bronze.raw_inadimplencia (arquivo_origem);
CREATE INDEX idx_inadimplencia_unidade ON bronze.raw_inadimplencia (unidade_bloco);
CREATE INDEX idx_inadimplencia_venc ON bronze.raw_inadimplencia (data_vencimento_original);

-- =============================================================================
-- PERMISSÕES DE ACESSO PARA API SUPABASE (POSTGREST)
-- =============================================================================
GRANT USAGE ON SCHEMA bronze, silver, gold TO anon, authenticated, service_role;

GRANT ALL ON ALL TABLES IN SCHEMA bronze TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA bronze TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA bronze 
GRANT ALL ON TABLES TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA bronze 
GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;

NOTIFY pgrst, 'reload config';
NOTIFY pgrst, 'reload schema';