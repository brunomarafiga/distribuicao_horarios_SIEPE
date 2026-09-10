# Ensalamento SIEPE - UFPR

Sistema automatizado de alocação de ensalamento para o evento **SIEPE** (Semana Integrada de Ensino, Pesquisa e Extensão) da **UFPR** (Universidade Federal do Paraná).

Este script Python foi desenvolvido para processar a base de dados de trabalhos aprovados no evento e realizar a distribuição otimizada deles pelas salas e blocos do campus de Curitiba. 

## 🎯 Objetivo e Regras de Negócio
O algoritmo de ensalamento (`ensalamento_siepe.py`) foi estruturado para respeitar as seguintes premissas acadêmicas:

1. **Agrupamento Temático**: O algoritmo busca maximizar a coerência das sessões, ancorando trabalhos de uma mesma **Área Temática** em uma sala fixa ao longo da semana.
2. **Prevenção de Choque de Horários (Submissores)**: O sistema evita que o mesmo professor (submissor) seja alocado para apresentar em duas salas diferentes no mesmo horário, e evita que seus trabalhos sejam empilhados numa única sala no mesmo momento. Os trabalhos são distribuídos de forma inteligente em dias/sessões diferentes mantendo a coerência da Área Temática.
3. **Exceções Hardcoded (Regra de Negócio)**:
   - **PET Litoral** e **Demanda 01** possuem uma obrigatoriedade de apresentação na **Segunda-feira (Sessão 3 - Tarde)**. Devido a restrição matemática do número de salas vs número de trabalhos, esses casos específicos contornam o bloqueio de empilhamento.
4. **Capacidade**: Máximo de 4 trabalhos por sala/sessão (com 20 minutos de discussão final). O sistema faz fallback para 5 trabalhos (16 min de exposição) caso as salas se esgotem.

## 🛠️ Como Utilizar

1. **Requisitos**: Python 3 e a biblioteca `pandas`.
2. **Arquivos de Entrada**: Coloque na mesma pasta ou na pasta pai os arquivos:
   - `lista de resumos.xls` (Matriz principal do evento gerada pelo sistema SIGA).
   - `EPEx-PG.xls` (Base de dados de Projetos de Extensão da Pós-Graduação).
3. **Execução**:
   ```bash
   python3 ensalamento_siepe.py
   ```

## 📦 Saídas (Entregáveis)
Como este repositório possui `.gitignore` para dados sensíveis, os artefatos de saída não são versionados. Ao executar o script, os seguintes arquivos serão gerados localmente:

- `03_Distribuicao_Horarios_SIEPE.zip`: Pacote oficial comprimido contendo a árvore de diretórios (Dia > Sessão > Salas) no formato `.csv` para publicação/distribuição.
- `ensalamento_curitiba_971.xlsx`: Relatório gerencial em Excel contendo tabelas dinâmicas com os resumos das sessões e o dimensionamento total de salas.
- `horarios_salas_resumos.csv`: Banco de dados limpo para fácil integração sistêmica (com `Código do Resumo`, `Bloco` e `Área Temática`).

## ⚙️ Arquitetura (Score-based Allocation)
Em vez de depender de processamento de filas (`fila_pendentes`) que acaba misturando áreas temáticas, o script utiliza um sistema de pontuação (`Score-based Allocation`) avaliando em tempo real todos os 242 espaços de sessões disponíveis na semana, recompensando salas tematicamente compatíveis (`+1000 pontos`) e penalizando misturas (`-1000 pontos`).
