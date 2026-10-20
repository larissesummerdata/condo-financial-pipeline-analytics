# 🏢 Condo Financial Pipeline Analytics: Pipeline ELT & Auditoria Contábil

> Pipeline ELT em nuvem (Python + Supabase PostgreSQL) para ingestão automatizada, higienização contábil e auditoria analítica de prestações de contas condominiais a partir de documentos extensos e desestruturados.

---

## Contexto & Motivação

Mensalmente, as administrações condominiais disponibilizam prestações de contas em arquivos PDF que frequentemente ultrapassam 200 páginas. Na prática, esses documentos reúnem uma colcha de retalhos de diferentes origens e formatações:

- Relatórios sintéticos de receitas e despesas com sumarizações agregadas;
- Extratos bancários contínuos sem linhas delimitadoras de tabela;
- Centenas de páginas anexas reunindo comprovantes avulsos de PIX, TED, faturas de concessionárias e notas fiscais.

Essa dispersão gera uma barreira crítica para os condôminos acompanharem o destino exato de suas contribuições mensais. Conferir página por página para entender o destino da arrecadação ou fiscalizar a conformidade dos pagamentos é inviável no dia a dia.

Este projeto nasceu de uma necessidade real no condomínio onde resido: **estruturar, sanear e conciliar 100% dos dados financeiros locais**, eliminando a assimetria de informação. O objetivo é transformar pilhas de documentos desestruturados em uma base de dados governada, viabilizando relatórios visuais claros e acessíveis para que eu ou qualquer condômino possa entender as contas, avaliar os gastos e participar ativamente de decisões em assembleia, inclusive em discussões sobre reajuste ou redução da taxa condominial.

---

## Objetivos de Engenharia & Negócio

1. **Democratização da Informação:** Converter relatórios contábeis densos em visualizações diretas de fluxo de caixa e comportamento de despesas (fixas e variáveis), embasando decisões coletivas sobre a alocação de recursos.
2. **Rastreabilidade Forense Contínua:** Mapear em cada registro carregado o nome do arquivo-fonte e o **número exato da página de origem**, viabilizando auditoria visual instantânea contra os comprovantes anexos.
3. **Validação Matemática Centesimal:** Implementar testes de conciliação pré-carga que garantem que o somatório dos lançamentos analíticos feche exatamente no centavo com os totais declarados pela administração.
4. **Infraestrutura em Nuvem Gerenciada:** Centralizar os dados no PostgreSQL gerenciado do Supabase através de schemas dedicados, garantindo governança relacional sem a necessidade de manter servidores locais.

---

## Arquitetura da Solução

O pipeline adota o padrão **Medallion Architecture (Bronze ➔ Silver ➔ Gold)** centralizado no PostgreSQL (Supabase):

```text
[ 1. Ingestão & RAW ] ➔ [ 2. Silver (Transformação) ] ➔ [ 3. Gold (Analytics) ] ➔ [ 4. Consumo ]
