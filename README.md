# Condo Financial Pipeline Analytics: Pipeline ELT & Auditoria Contábil

> Pipeline ELT em nuvem (Python + Supabase PostgreSQL) para ingestão automatizada, higienização contábil e auditoria analítica de prestações de contas condominiais a partir de documentos extensos e desestruturados.

---

## Contexto & Motivação

Mensalmente, administrações condominiais emitem prestações de contas consolidadas em arquivos PDF que ultrapassam 200 páginas. Na prática, esses documentos reúnem uma colcha de retalhos com diferentes níveis de formatação:

- Relatórios sintéticos de receitas e despesas;
- Extratos de conta bancária sem grade delimitadora de tabela;
- Centenas de páginas anexas com comprovantes avulsos de PIX, TED, faturas de concessionárias e notas fiscais.

Essa dispersão gera uma barreira crítica de transparência: conferir página por página para auditar a conformidade de pagamentos e entender a real destinação das taxas condominiais é uma tarefa inviável no dia a dia dos moradores e do conselho fiscal.

Este projeto nasceu de uma necessidade real: **estruturar, sanear e conciliar 100% dos dados financeiros do condomínio onde resido**, eliminando a assimetria de informação. A iniciativa constrói uma base governada que viabiliza relatórios visuais claros, permitindo aos condôminos compreenderem a distribuição de despesas essenciais e embasarem decisões assertivas sobre reajustes ou reduções de taxa em assembleia.

---

## Objetivos de Engenharia & Negócio

1. **Acessibilidade & Democratização da Informação:** Traduzir centenas de páginas contábeis em visões intuitivas de fluxo de caixa, evolução de custos fixos/variáveis e suporte à alocação estratégica de recursos.
2. **Rastreabilidade Forense Contínua:** Preservar em cada linha carregada o nome do arquivo original e o **número exato da página**, viabilizando auditoria visual imediata contra o documento comprobatório.
3. **Validação Matemática Centesimal:** Aplicar testes de conciliação pré-carga que conferem se o somatório dos lançamentos analíticos coincide exatamente no centavo com os cabeçalhos declarados pela administração.
4. **Infraestrutura em Nuvem Gerenciada:** Arquitetura 100% cloud baseada em schemas nativos do PostgreSQL (Supabase), garantindo persistência relacional governada sem custos com servidores dedicados.

---

## Arquitetura da Solução

O fluxo de dados segue o padrão **Medallion Architecture (Bronze ➔ Silver ➔ Gold)** centralizado no Supabase, garantindo segregação de responsabilidades desde o dado bruto até a camada de consumo:

```text
[ 1. Ingestão & RAW ] ➔ [ 2. Silver (Transformação) ] ➔ [ 3. Gold (Analytics) ] ➔ [ 4. Consumo ]
