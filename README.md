<div align="center">

# 🗓️ Ensalamento Otimizado SIEPE — UFPR
### Algoritmo Automatizado de Distribuição e Alocação de Salas e Horários

**Otimização Combinatória e Gestão Logística para a Semana Integrada de Ensino, Pesquisa e Extensão da UFPR**

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Instituição](https://img.shields.io/badge/Evento-SIEPE%20%2F%20UFPR-004587)](https://www.ufpr.br)
[![Algoritmo](https://img.shields.io/badge/M%C3%A9todo-Otimiza%C3%A7%C3%A3o%20Heur%C3%ADstica%20%26%20Aloca%C3%A7%C3%A3o-orange)](#-regras-de-negócio-e-critérios)
[![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-success)](#)

</div>

---

## 📌 Visão Geral

A **Semana Integrada de Ensino, Pesquisa e Extensão (SIEPE)** é o maior evento acadêmico anual da Universidade Federal do Paraná (UFPR), reunindo simultaneamente milhares de apresentações de iniciação científica (EVINCI), extensão (EAF) e inovação.

A distribuição manual desses trabalhos em centenas de salas físicas, respeitando restrições de horários de orientadores, afinidades temáticas e capacidades de auditório, é um problema de otimização complexo. 

Este projeto disponibiliza um algoritmo em Python (`ensalamento_siepe.py`) desenvolvido para realizar a alocação de ensalamento com **zero choques de horários** e **máxima coerência temática**.

---

## 🎯 Regras de Negócio e Critérios

O algoritmo foi calibrado para satisfazer as seguintes restrições acadêmicas e logísticas:

1. **Prevenção Rígida de Choque de Horários:**
   - O mesmo orientador/submissor nunca é agendado em duas salas distintas no mesmo bloco de tempo.
   - Distribuição equilibrada de bancas ao longo dos turnos matutino e vespertino.
2. **Ancoragem e Coerência Temática:**
   - Trabalhos de uma mesma grande área (Exatas, Humanas, Biológicas, Saúde) são agrupados no mesmo bloco predial e salas correlatas.
3. **Otimização de Ocupação:**
   - Minimização de salas subutilizadas ou sessões esparsas, concentrando o público e otimizando a escala dos avaliadores.

---

## 📂 Arquivos do Projeto

```text
├── ensalamento_siepe.py         # Script principal com a lógica heurística de alocação
├── demandas_ensalamento.md      # Especificação das restrições, matriz de capacidade e premissas
├── .gitignore                   # Proteção de bases de dados sensíveis de inscritos
└── README.md                    # Documentação técnica e operacional
```

---

## 🚀 Como Executar

```bash
git clone https://github.com/brunomarafiga/distribuicao_horarios_SIEPE.git
cd distribuicao_horarios_SIEPE
python -m pip install pandas openpyxl
```

Para processar a base de inscritos e gerar o mapa de ensalamento:
```bash
python ensalamento_siepe.py
```

---

<div align="center">
Desenvolvido por <strong>Bruno Marafiga</strong><br>
Curso de Gestão da Informação • Universidade Federal do Paraná (UFPR)
</div>
