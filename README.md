# Condo Financial Pipeline Analytics: Pipeline ELT & Auditoria Contábil

> Pipeline ELT em nuvem (Python + Supabase PostgreSQL) para ingestão automatizada, higienização contábil e auditoria analítica de prestações de contas condominiais a partir de documentos extensos e desestruturados.

---

## Contexto & Motivação

Mensalmente, administrações condominiais emitem prestações de contas consolidadas em arquivos PDF que ultrapassam 200 páginas. Na prática, esses documentos reúnem uma colcha de retalhos com diferentes níveis de formatação:

- Relatórios sintéticos de receitas e despesas;
- Extratos de conta bancária sem grade delimitadora de tabela;
- Centenas de páginas anexas com comprovantes avulsos de PIX, TED, faturas de concessionárias e notas fiscais.

Essa dispersão gera uma barreira crítica de leitura para condôminos conhecerem para onde vai a sua contribuição de taxa e outras despesas . Conferir manualmente página por página para entender o destino da arrecadação ou fiscalizar a conformidade dos pagamentos é uma tarefa inviável no dia a dia.

Este projeto nasceu de uma necessidade real: **estruturar, sanear e conciliar 100% dos dados financeiros do condomínio onde resido**, eliminando a assimetria de informação e construindo uma base de dados governada capaz de alimentar relatórios visuais claros, intuitivos e acessíveis para qualquer condômino conhecer e entender as receitas e necessidade de gastos de seu condominio, ate mesmo para conseguir discutir sobre aumento ou redução da taxa de condomínio.

---

## Objetivos de Engenharia & Negócio

1. **Acessibilidade & Democratização da Informação:** Traduzir centenas de páginas contábeis em visões diretas de fluxo de caixa, evolução de despesas fixas, variáveis e poder decidir sobre a alocação dos recursos financeiros.
2. **Rastreabilidade Forense Contínua:** Preservar em cada linha carregada o nome do arquivo original e o **número exato da página**, permitindo auditoria visual imediata contra o documento comprobatório.
3. **Validação Matemática Centesimal:** Aplicar testes de conciliação pré-carga que conferem se a soma dos lançamentos analíticos bate exatamente no centavo com os cabeçalhos declarados pela administração.
4. **Infraestrutura em Nuvem Gerenciada:** Arquitetura 100% cloud baseada em schemas nativos do PostgreSQL (Supabase), garantindo persistência estruturada sem custos de servidores locais.

---

## Arquitetura da Solução

O fluxo de dados segue o padrão **Medallion Architecture (Bronze ➔ Silver ➔ Gold)**, implementado via schemas dedicados no PostgreSQL:

[ 1. Ingestão & RAW ] ➔ [ 2. Silver (Transformação) ] ➔ [ 3. Gold (Analytics) ] ➔ [ 4. Consumo ]

---

## Estrutura do Repositório

```text
├── sql/
│   └── setup_schemas.sql     # DDL de criação e permissões dos schemas (bronze, silver, gold)
├── src/
│   ├── __init__.py           # Inicializador do pacote Python
│   ├── connection.py         # Gerenciamento de conexão segura com a API do Supabase
│   ├── extractors.py         # Motores de parsing (pdfplumber, regex de extrato e tabelas)
│   └── main.py               # Orquestrador do pipeline de carga na camada Bronze
├── .gitignore                # Bloqueio de arquivos sensíveis (.env, *.pdf, *.duckdb)
├── README.md                 # Documentação arquitetural e estudo de caso
└── requirements.txt          # Dependências do projeto (supabase, pdfplumber, python-dotenv)

