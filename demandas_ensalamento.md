# Registro de Demandas Especiais - Ensalamento SIEPE

Este documento registra as exceções e pedidos especiais de alocação de horários que foram hardcoded no script de ensalamento (`ensalamento_siepe.py`) para garantir o atendimento às necessidades logísticas dos submissores.

## Demandas Registradas

### 1. Demanda Institucional: PET Litoral e Demanda 01
- **Regra**: Fixar apresentação na **Segunda-feira, Sessão 3 (Tarde)**.
- **Motivo**: Logística de transporte e organização pré-definida pela PROGRAD.
- **Status**: Implementado no algoritmo (`Is_PET_Litoral` e `Is_Demanda01`).

### 2. Demanda Profa. Renata Dal-Prá Ducci
- **Data do Pedido**: 17/09/2026
- **Trabalho**: Liga Acadêmica de Neurociências - NeuroLiga UFPR (Código: 202626399)
- **Regra Solicitada**: Alocação exclusiva na **Terça-feira pela manhã (Sessão 1)**.
- **Motivo**: Conflito de agenda médica no CHC UFPR e apresentação em Iniciação Científica na sexta-feira.
- **Status**: Implementado no algoritmo (`Is_Renata`). Trabalho forçado para a sala PA-04, isolado do fluxo geral para evitar sobrescritas.
