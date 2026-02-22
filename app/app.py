from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Tuple, List

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


# ----------------------------
# Config
# ----------------------------
st.set_page_config(
    page_title="Passos Mágicos • Risco de Defasagem (IAN)",
    page_icon="📈",
    layout="wide",
)

CSS = """
<style>
/* Container */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* Sidebar */
section[data-testid="stSidebar"] { padding-top: 0.5rem; }

/* KPI cards */
.kpi {
  border: 1px solid rgba(49, 51, 63, 0.15);
  border-radius: 16px;
  padding: 16px 18px;
  background: rgba(255,255,255,0.03);
}
.kpi .label { font-size: 12px; opacity: 0.85; margin-bottom: 6px; letter-spacing: 0.2px;}
.kpi .value { font-size: 26px; font-weight: 750; line-height: 1.0; }
.kpi .sub { font-size: 12px; opacity: 0.8; margin-top: 6px; }

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(49, 51, 63, 0.15);
  margin-right: 6px;
  opacity: 0.92;
}

hr { margin: 1rem 0; opacity: 0.25; }

/* Links discretos */
a { text-decoration: none; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ----------------------------
# Helpers
# ----------------------------
DEFAULT_PATHS = [
    "predicoes_risco_ian.csv",
    "outputs/predicoes_risco_ian.csv",
]

PROB_COL_DEFAULT = "proba_risco_ian"
PRED_COL_DEFAULT = "pred_risco_ian"


@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def fmt_float(x: float, nd: int = 4) -> str:
    return f"{x:.{nd}f}"


def pick_existing(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def ensure_types(df: pd.DataFrame, prob_col: str, pred_col: str) -> pd.DataFrame:
    out = df.copy()
    out[prob_col] = pd.to_numeric(out[prob_col], errors="coerce")
    out[pred_col] = pd.to_numeric(out[pred_col], errors="coerce").fillna(0).astype(int)

    # ano numérico se existir
    if "ANO" in out.columns:
        out["ANO"] = pd.to_numeric(out["ANO"], errors="coerce")

    return out


def validate_schema(df: pd.DataFrame) -> Tuple[bool, str]:
    missing = [c for c in [PROB_COL_DEFAULT, PRED_COL_DEFAULT] if c not in df.columns]
    if missing:
        return False, (
            f"CSV não possui colunas obrigatórias: {missing}. "
            f"Colunas encontradas: {df.columns.tolist()}"
        )
    return True, ""


def kpi_card(label: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="kpi">
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nice_badges(modelo: Optional[str], thr: Optional[float], n: int):
    parts = []
    if modelo:
        parts.append(f"<span class='badge'>Modelo: <b>{modelo}</b></span>")
    if thr is not None:
        parts.append(f"<span class='badge'>Threshold: <b>{thr:.2f}</b></span>")
    parts.append(f"<span class='badge'>Registros: <b>{fmt_int(n)}</b></span>")
    st.markdown(" ".join(parts), unsafe_allow_html=True)


def safe_series_count(df: pd.DataFrame) -> Tuple[str, str]:
    """Retorna colunas para contagem (preferindo RA, senão pred_col)."""
    if "RA" in df.columns:
        return "RA", "count"
    return PRED_COL_DEFAULT, "count"


def humanize_pred_label(x: str) -> str:
    return "Risco" if str(x) == "1" else "Sem risco"


# ----------------------------
# Sidebar: data source
# ----------------------------
st.sidebar.title("Painel")

st.sidebar.subheader("Fonte de dados")
uploaded = st.sidebar.file_uploader("Carregar CSV de predições", type=["csv"])

source_path = None
df_raw = None

if uploaded is not None:
    df_raw = pd.read_csv(uploaded)
else:
    source_path = next((p for p in DEFAULT_PATHS if Path(p).exists()), None)
    if source_path:
        df_raw = load_csv(source_path)

if df_raw is None:
    st.error("Não encontrei o CSV de predições. Envie um arquivo no painel lateral ou coloque `predicoes_risco_ian.csv` na raiz.")
    st.stop()

ok, msg = validate_schema(df_raw)
if not ok:
    st.error(msg)
    st.stop()

prob_col = PROB_COL_DEFAULT
pred_col = PRED_COL_DEFAULT

df_raw = ensure_types(df_raw, prob_col, pred_col)

# meta (opcional no CSV)
modelo_usado = pick_existing(df_raw, ["modelo_usado", "MODEL", "model"])
threshold_col = pick_existing(df_raw, ["threshold_usado", "threshold", "THRESHOLD"])

thr_value = None
if threshold_col:
    try:
        thr_value = float(pd.to_numeric(df_raw[threshold_col], errors="coerce").dropna().iloc[0])
    except Exception:
        thr_value = None

# ----------------------------
# Sidebar: filters
# ----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Segmentação")

filter_cols = ["ANO", "FASE", "TURMA", "PEDRA", "INSTITUICAO_DE_ENSINO", "GENERO"]
active_filters = {}

df = df_raw.copy()

# Ano: multiselect ou range
if "ANO" in df.columns and df["ANO"].notna().any():
    years = sorted(df["ANO"].dropna().astype(int).unique().tolist())
    if years:
        year_mode = st.sidebar.radio("Filtro de ANO", ["Todos", "Selecionar", "Intervalo"], horizontal=True)
        if year_mode == "Selecionar":
            sel = st.sidebar.multiselect("Anos", years, default=years)
            df = df[df["ANO"].isin(sel)]
            active_filters["ANO"] = sel
        elif year_mode == "Intervalo":
            mn, mx = min(years), max(years)
            a, b = st.sidebar.slider("Intervalo de anos", mn, mx, (mn, mx))
            df = df[(df["ANO"] >= a) & (df["ANO"] <= b)]
            active_filters["ANO"] = [a, b]

# Outros filtros
for c in [x for x in filter_cols if x != "ANO"]:
    if c in df.columns:
        opts = sorted(df[c].dropna().astype(str).unique().tolist())
        if opts:
            sel = st.sidebar.multiselect(c, opts, default=opts)
            df = df[df[c].astype(str).isin(sel)]
            active_filters[c] = sel

st.sidebar.markdown("---")
top_n = st.sidebar.slider("Top N (maior risco)", 5, 200, 20)

# Busca RA/NOME
search_cols = [c for c in ["RA", "NOME"] if c in df.columns]
q = st.sidebar.text_input("Buscar (RA/NOME)", value="").strip()
if q and search_cols:
    pattern = re.escape(q.lower())
    mask = False
    for c in search_cols:
        mask = mask | df[c].astype(str).str.lower().str.contains(pattern, na=False)
    df = df[mask]


# ----------------------------
# Header
# ----------------------------
st.title("📈 Risco de Defasagem (IAN) • Priorização de Intervenção")

st.caption(
    "Painel de apoio à priorização de acompanhamento pedagógico. "
    "Exibe a probabilidade de risco (0–1) e a classificação (0/1) geradas pelo modelo, "
    "com filtros e ranking para identificar alunos prioritários."
)

modelo_label = None
if modelo_usado and df_raw[modelo_usado].notna().any():
    modelo_label = str(df_raw[modelo_usado].dropna().iloc[0])

nice_badges(modelo_label, thr_value, len(df))

st.markdown("<hr/>", unsafe_allow_html=True)


# ----------------------------
# Tabs
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Visão geral", "Explorar", "Insights", "Sobre"])


# ----------------------------
# Tab 1: Overview
# ----------------------------
with tab1:
    total = len(df)
    pos = int((df[pred_col] == 1).sum())
    rate = (pos / total) if total else 0.0
    med = float(df[prob_col].median()) if total else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Registros no recorte", fmt_int(total), "Após filtros e busca")
    with c2:
        kpi_card("Alvos prioritários", fmt_int(pos), "predição risco = 1")
    with c3:
        kpi_card("Taxa de risco", fmt_pct(rate), "proporção de risco no recorte")
    with c4:
        kpi_card("Mediana da probabilidade", fmt_float(med, 4), "distribuição geral")

    st.markdown("<hr/>", unsafe_allow_html=True)

    colA, colB = st.columns([1.2, 1.0])

    with colA:
        st.subheader("Distribuição das probabilidades")
        fig = px.histogram(
            df.dropna(subset=[prob_col]),
            x=prob_col,
            nbins=40,
            labels={prob_col: "Probabilidade de risco (IAN)", "count": "Quantidade"},
            title=None,
        )
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.subheader("Distribuição das classes previstas")
        counts = df[pred_col].value_counts().sort_index()
        df_counts = pd.DataFrame({pred_col: counts.index.astype(str), "count": counts.values})
        df_counts[pred_col] = df_counts[pred_col].map(humanize_pred_label)

        fig2 = px.bar(
            df_counts,
            x=pred_col,
            y="count",
            text="count",
            labels={pred_col: "Classe prevista", "count": "Quantidade"},
            title=None,
        )
        fig2.update_traces(textposition="outside", cliponaxis=False)
        fig2.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    if "ANO" in df.columns and df["ANO"].notna().any():
        st.subheader("Taxa de risco por ano")
        count_col, count_agg = safe_series_count(df)

        tmp = (
            df.dropna(subset=["ANO"])
            .assign(ANO=df["ANO"].astype(int))
            .groupby("ANO")
            .agg(
                total=(count_col, count_agg),
                positivos=(pred_col, "sum"),
                proba_media=(prob_col, "mean"),
            )
            .reset_index()
        )
        tmp["taxa_risco"] = tmp["positivos"] / tmp["total"]

        fig3 = px.line(
            tmp,
            x="ANO",
            y="taxa_risco",
            markers=True,
            labels={"ANO": "Ano", "taxa_risco": "Taxa de risco"},
        )
        fig3.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)


# ----------------------------
# Tab 2: Explorer
# ----------------------------
with tab2:
    st.subheader(f"Top {top_n} maiores riscos")
    st.caption("Lista dos alunos com maior probabilidade no recorte atual, útil para priorização e acompanhamento.")

    id_cols = [c for c in ["RA", "NOME", "ANO", "FASE", "TURMA", "PEDRA", "INSTITUICAO_DE_ENSINO", "GENERO"] if c in df.columns]
    show_cols = id_cols + [prob_col, pred_col]

    # manter metadados se existirem
    if threshold_col:
        show_cols.append(threshold_col)
    if modelo_usado:
        show_cols.append(modelo_usado)

    # remove duplicados preservando ordem
    show_cols = list(dict.fromkeys(show_cols))

    top_df = df.sort_values(prob_col, ascending=False).head(top_n)[show_cols].copy()
    if pred_col in top_df.columns:
        top_df[pred_col] = top_df[pred_col].astype(int)

    left, right = st.columns([1.6, 1.0])

    with left:
        st.dataframe(top_df, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Baixar CSV do recorte (com filtros)",
            df.to_csv(index=False).encode("utf-8"),
            file_name="predicoes_risco_ian_filtrado.csv",
            mime="text/csv",
        )

    with right:
        st.subheader("Ranking (Top N)")
        fig = px.bar(
            top_df.reset_index(drop=True),
            x=top_df.reset_index(drop=True).index + 1,
            y=prob_col,
            labels={prob_col: "Probabilidade de risco (IAN)"},
        )
        fig.update_layout(
            height=380,
            xaxis_title="Posição no ranking",
            yaxis_title="Probabilidade",
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# Tab 3: Insights
# ----------------------------
with tab3:
    st.subheader("Insights do recorte atual")
    st.caption(
        "Resumo do comportamento do risco no recorte selecionado. "
        "Use esta aba para identificar concentrações de risco e perfis prioritários."
    )

    if len(df) > 0:
        p90 = float(df[prob_col].quantile(0.90))
        p95 = float(df[prob_col].quantile(0.95))
        st.markdown(
            f"- **P90** da probabilidade: `{p90:.4f}`  \n"
            f"- **P95** da probabilidade: `{p95:.4f}`  \n"
            f"- **Taxa de risco (pred=1)** no recorte: `{(df[pred_col]==1).mean()*100:.2f}%`"
        )

    st.markdown("<hr/>", unsafe_allow_html=True)

    candidate_groups = [c for c in ["FASE", "PEDRA", "INSTITUICAO_DE_ENSINO", "TURMA", "GENERO"] if c in df.columns]
    if candidate_groups:
        group_col = st.selectbox("Analisar por", candidate_groups, index=0)

        agg = (
            df.groupby(group_col, dropna=False)
            .agg(
                total=(pred_col, "count"),
                positivos=(pred_col, "sum"),
                proba_media=(prob_col, "mean"),
                proba_mediana=(prob_col, "median"),
            )
            .reset_index()
        )
        agg["taxa_risco"] = agg["positivos"] / agg["total"]
        agg = agg.sort_values("taxa_risco", ascending=False).head(20)

        c1, c2 = st.columns([1.1, 1.0])
        with c1:
            st.subheader("Grupos com maior taxa de risco")
            show = agg.copy()
            show["taxa_risco"] = show["taxa_risco"].astype(float)
            st.dataframe(show, use_container_width=True, hide_index=True)

        with c2:
            fig = px.bar(
                agg,
                x=group_col,
                y="taxa_risco",
                hover_data=["total", "positivos", "proba_media", "proba_mediana"],
                labels={group_col: group_col, "taxa_risco": "Taxa de risco"},
            )
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Para insights por perfil, inclua no CSV colunas como FASE/PEDRA/TURMA/INSTITUICAO_DE_ENSINO/GENERO.")


# ----------------------------
# Tab 4: About
# ----------------------------
with tab4:
    st.subheader("Sobre o Projeto Passos Mágicos")
    st.markdown(
        """
O **Passos Mágicos** é uma iniciativa socioeducacional que acompanha o desenvolvimento de alunos ao longo do tempo.
A evolução é observada por indicadores como **IAN** (defasagem), **IDA** (desempenho), **IEG** (engajamento),
**IAA** (autoavaliação), **IPS** (psicossocial), **IPP** (psicopedagógico), **IPV** (ponto de virada) e o índice consolidado **INDE**.

Este painel foi construído para apoiar a tomada de decisão, ajudando a **priorizar intervenções** com base em probabilidades
estimadas de risco de defasagem (IAN) no recorte selecionado.
"""
    )

    st.subheader("Sobre o modelo e como usar")
    st.markdown(
        """
**O que este app entrega?**  
Uma visão operacional das predições do modelo, com filtros e ranking para apoiar a priorização de acompanhamento.

**Como interpretar as colunas principais**  
- `proba_risco_ian`: probabilidade (0 a 1). Quanto maior, maior a prioridade.
- `pred_risco_ian`: classificação (0/1) aplicada com base em um threshold.
- `threshold_usado` / `modelo_usado`: metadados opcionais (quando presentes no CSV).

**Fluxo recomendado**
1) Aplique filtros (ANO/FASE/PEDRA/TURMA/ESCOLA) para segmentar o recorte.
2) Use o **Top N** para identificar os alunos com maior probabilidade.
3) Exporte o CSV filtrado para compartilhar com a equipe e registrar plano de ação.
"""
    )

    with st.expander("Amostra do CSV (diagnóstico)"):
        st.write(df_raw.head(10))
        st.write("Colunas:", df_raw.columns.tolist())