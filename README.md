# passos_magicos_datathon_fase5

Projeto desenvolvido para o **POSTECH – DTAT – Datathon – Fase 5 (Passos Mágicos)**, combinando:
- **Dashboard analítico (Power BI)**
- **Modelo de Machine Learning** para risco de defasagem (IAN)
- **Aplicação Streamlit** para exploração e priorização de intervenção

---

## 🧩 Descrição

O objetivo é analisar a evolução dos indicadores educacionais do **Projeto Passos Mágicos** e gerar uma solução que apoie a **priorização de acompanhamento** para alunos com maior risco de defasagem (**IAN**).

O projeto utiliza indicadores como:
- **IAN** (Defasagem)
- **IDA** (Desempenho)
- **IEG** (Engajamento)
- **IAA** (Autoavaliação)
- **IPS** (Psicossocial)
- **IPP** (Psicopedagógico)
- **IPV** (Ponto de Virada)
- **INDE** (Índice consolidado)

---

## 📌 Entregáveis

- ✅ **Power BI**: painel com storytelling e respostas das perguntas do desafio  
- ✅ **Notebook(s)**: EDA, construção do datamart, treino e avaliação do modelo  
- ✅ **Pipeline**: modelo salvo em `models/` e inferência para gerar predições  
- ✅ **Streamlit**: app para explorar risco, filtrar e exportar lista priorizada  

> Links (preencha com os seus):
- **Power BI (publicado):** `<cole aqui>`
- **Streamlit (publicado):** `<cole aqui>`

---

## 📁 Estrutura do projeto

```text
.
├─ app/
│   └─ app.py                       # Aplicação Streamlit
├─ bi/
│   └─ ANALISE_BI_TECH5.pdf          # Export do dashboard (backup/versão final)
├─ data/
│   ├─ BASE DE DADOS PEDE 2024 - DATATHON.xlsx
│   ├─ datamart_wide_aluno_ano.csv   # Saída do datamart (aluno-ano)
│   ├─ datamart_long_indicadores.csv # Saída long (indicadores empilhados)
│   └─ predicoes_risco_ian.csv       # Saída do pipeline (probabilidade + classe)
├─ models/
│   └─ ian_risk_pipeline.joblib      # Bundle do modelo (pipeline + threshold + metadados)
├─ notebooks/
│   ├─ 01_eda.ipynb                  # Exploração inicial e entendimento do dataset
│   ├─ 02_build_datamart.ipynb        # Construção do datamart (wide/long)
│   ├─ 03_model_training.ipynb        # Treino/avaliação + salvamento do modelo
│   └─ 04_pipeline.ipynb             # Inferência e geração do CSV de predições
├─ requirements.txt
└─ README.md
