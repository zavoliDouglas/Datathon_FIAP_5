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

🤖 Modelo de Machine Learning

Tarefa: Classificação binária de risco de defasagem (IAN)

Target: TARGET_RISCO_IAN (definido via comparação temporal entre anos do mesmo aluno)

Saída do modelo:

proba_risco_ian (0–1)

pred_risco_ian (0/1 usando threshold escolhido)

Pipeline:

Pré-processamento com ColumnTransformer

OneHotEncoder para colunas categóricas

Imputer/Scaler (conforme o notebook)

Modelos testados (ex.): Logistic Regression, Random Forest

Métricas registradas no notebook: Accuracy, F1, ROC-AUC, matriz de confusão

Threshold selecionado para priorização (ex.: melhor F1/recall)

O modelo final é salvo como bundle em:

models/ian_risk_pipeline.joblib

📊 Dashboard (Power BI)

O painel foi estruturado para responder às perguntas do desafio com visual limpo e leitura rápida, incluindo:

Visão geral (INDE, Pedras, evolução)

Indicadores-chave (IAN, IDA, IEG, IAA, IPS, IPP)

Drivers do INDE e segmentações

IPV (ponto de virada) e relações com engajamento/desempenho

Evidência temporal (IPS t-1 vs queda em IDA/IEG)

Backup do painel exportado em:

bi/ANALISE_BI_TECH5.pdf

🌐 Aplicação Web (Streamlit)

A aplicação app/app.py permite:

Carregar/usar predicoes_risco_ian.csv

Filtrar por ano e segmentações disponíveis

Visualizar distribuição de risco (probabilidades e classes)

Ver ranking Top N com maior risco

Exportar CSV filtrado para priorização de intervenção

▶️ Como executar o projeto
1) Clonar o repositório
git clone <SEU_REPO_AQUI>
cd <PASTA_DO_REPO>
2) Criar ambiente virtual (opcional)
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
3) Instalar dependências
pip install -r requirements.txt
4) Gerar o datamart (se necessário)

Execute:

notebooks/02_build_datamart.ipynb

Isso gera:

data/datamart_wide_aluno_ano.csv

data/datamart_long_indicadores.csv

5) Treinar e salvar o modelo

Execute:

notebooks/03_model_training.ipynb

Isso gera:

models/ian_risk_pipeline.joblib

6) Rodar inferência e gerar predições

Execute:

notebooks/04_pipeline.ipynb

Isso gera:

data/predicoes_risco_ian.csv

7) Rodar o Streamlit
streamlit run app/app.py

Acesse:

http://localhost:8501
👤 Autor

Projeto desenvolvido por Douglas para o POSTECH – DTAT – Datathon – Fase 5 (Passos Mágicos).
