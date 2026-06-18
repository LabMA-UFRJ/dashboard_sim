from __future__ import annotations
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, List
import plotly.graph_objects as go

st.set_page_config(
    layout="wide",
    page_title="Análise de Mortalidade SIM-DATASUS",
)

PROCESSED_DIR = Path("./data/processed")

CATEGORY_LABELS = {
    "total": "Total",
    "genero": "Gênero",
    "raca_cor": "Raça/Cor",
    "uf": "UF",
}

COLOR_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


# ============================================================================
# DATA LOADING
# ============================================================================

def get_available_years() -> List[int]:
    if not PROCESSED_DIR.exists():
        return []
    return sorted(
        int(d.name) for d in PROCESSED_DIR.iterdir()
        if d.is_dir() and d.name.isdigit()
    )


@st.cache_data
def load_year_data(year: int) -> Dict[str, Dict[str, pd.DataFrame]]:
    """Load all mx CSVs for a given year as {category: {label: df}}."""
    year_dir = PROCESSED_DIR / str(year)
    data: Dict[str, Dict[str, pd.DataFrame]] = {}
    if not year_dir.exists():
        return data
    for cat_dir in sorted(year_dir.iterdir()):
        if not cat_dir.is_dir():
            continue
        cat_data: Dict[str, pd.DataFrame] = {}
        for csv_file in sorted(cat_dir.glob("mx_*.csv")):
            label = csv_file.stem[len("mx_"):]
            try:
                df = pd.read_csv(csv_file)
                df.columns = df.columns.str.strip()
                cat_data[label] = df
            except Exception as e:
                st.warning(f"Erro ao ler {csv_file.name}: {e}")
        if cat_data:
            data[cat_dir.name] = cat_data
    return data


# ============================================================================
# STATISTICS
# ============================================================================

def calculate_statistics(dfs: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    stats = {}
    for label, df in dfs.items():
        if "mx" not in df.columns:
            continue
        mx = df["mx"].dropna()
        stats[label] = {
            "Média": mx.mean(),
            "Mediana": mx.median(),
            "Mínimo": mx.min(),
            "Máximo": mx.max(),
            "Desvio Padrão": mx.std(),
            "Total de Óbitos": int(df["deaths"].sum()) if "deaths" in df.columns else 0,
            "Total de Exposição": int(df["population"].sum()) if "population" in df.columns else 0,
        }
    return stats


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_mx_lines(dfs: Dict[str, pd.DataFrame], title: str) -> None:
    """Overlay mx age curves for all groups in a category (log-scale)."""
    fig = go.Figure()
    for i, (label, df) in enumerate(dfs.items()):
        if "mx" not in df.columns or "idade" not in df.columns:
            continue
        plot_data = df[df["mx"] > 0].sort_values("idade")
        fig.add_trace(go.Scatter(
            x=plot_data["idade"],
            y=plot_data["mx"],
            mode="lines",
            name=label.replace("_", " ").title(),
            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=1.8),
            hovertemplate=f"{label}<br>Idade: %{{x}}<br>Mx: %{{y:.6f}}<extra></extra>",
        ))
    fig.update_layout(
        title=title,
        xaxis=dict(title="Idade (anos)", range=[16, 100]),
        yaxis=dict(title="Mx (escala log)", type="log"),
        height=500,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_deaths_exposure(dfs: Dict[str, pd.DataFrame], title: str) -> None:
    """Overlay deaths and population by age for all groups in a category."""
    fig = go.Figure()
    for i, (label, df) in enumerate(dfs.items()):
        if "deaths" not in df.columns or "population" not in df.columns or "idade" not in df.columns:
            continue
        plot_data = df.sort_values("idade")
        fig.add_trace(go.Scatter(
            x=plot_data["idade"],
            y=plot_data["deaths"],
            mode="lines",
            name=f"{label} - Óbitos",
            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=1.5, dash="solid"),
            hovertemplate=f"{label} - Óbitos<br>Idade: %{{x}}<br>Óbitos: %{{y:,}}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=plot_data["idade"],
            y=plot_data["population"],
            mode="lines",
            name=f"{label} - Exposição",
            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=1.5, dash="dot"),
            hovertemplate=f"{label} - Exposição<br>Idade: %{{x}}<br>Exposição: %{{y:,}}<extra></extra>",
        ))
    fig.update_layout(
        title=title,
        xaxis=dict(title="Idade (anos)", range=[16, 100]),
        yaxis=dict(title="Contagem", type="linear"),
        height=500,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.title("📊 Análise de Mortalidade - Taxas (Mx) por Ano")
    st.markdown("Visualização das taxas de mortalidade (mx) do SIM-DATASUS por ano")

    years = get_available_years()
    if not years:
        st.error("❌ Nenhum dado processado encontrado em data/processed/")
        return

    selected_years: List[int] = st.sidebar.multiselect(
        "📅 Selecione o(s) Ano(s)",
        years,
        default=[years[-1]],
        help="Escolha um ou mais anos para sobrepor no mesmo gráfico",
    )

    if not selected_years:
        st.info("Selecione ao menos um ano na barra lateral.")
        return

    multi = len(selected_years) > 1

    all_year_data: Dict[int, Dict[str, Dict[str, pd.DataFrame]]] = {}
    for yr in selected_years:
        yd = load_year_data(yr)
        if yd:
            all_year_data[yr] = yd

    if not all_year_data:
        st.error("❌ Nenhum dado disponível para os anos selecionados.")
        return

    # Merge into {cat: {label [· year]: df}} so existing functions work unchanged
    merged: Dict[str, Dict[str, pd.DataFrame]] = {}
    for yr, year_data in all_year_data.items():
        for cat, dfs in year_data.items():
            merged.setdefault(cat, {})
            for label, df in dfs.items():
                key = f"{label} · {yr}" if multi else label
                merged[cat][key] = df

    year_str = ", ".join(str(y) for y in sorted(selected_years))
    st.success(f"✅ Dados carregados: {year_str}")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📈 Visualizações", "📊 Estatísticas", "📋 Dados"])

    with tab1:
        st.subheader(f"Visualizações — {year_str}")
        for cat, dfs in merged.items():
            cat_label = CATEGORY_LABELS.get(cat, cat.replace("_", " ").title())
            with st.expander(f"📊 {cat_label}", expanded=True):
                plot_mx_lines(dfs, f"Mx por Idade — {cat_label} ({year_str})")
                plot_deaths_exposure(dfs, f"Óbitos e Exposição por Idade — {cat_label} ({year_str})")

    with tab2:
        st.subheader(f"Estatísticas por Categoria — {year_str}")
        for cat, dfs in merged.items():
            cat_label = CATEGORY_LABELS.get(cat, cat.replace("_", " ").title())
            stats = calculate_statistics(dfs)
            if not stats:
                continue
            with st.expander(f"📈 {cat_label}", expanded=True):
                for label, s in stats.items():
                    st.markdown(f"**{label.replace('_', ' ').title()}**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Média Mx", f"{s['Média']:.6f}")
                    with col2:
                        st.metric("Mediana Mx", f"{s['Mediana']:.6f}")
                    with col3:
                        st.metric("Mínimo Mx", f"{s['Mínimo']:.6f}")
                    with col4:
                        st.metric("Máximo Mx", f"{s['Máximo']:.6f}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Desvio Padrão", f"{s['Desvio Padrão']:.6f}")
                    with col2:
                        st.metric("Total Óbitos", f"{s['Total de Óbitos']:,}")
                    with col3:
                        st.metric("Total Exposição", f"{s['Total de Exposição']:,}")
                    st.divider()

    with tab3:
        st.subheader(f"Dados Brutos — {year_str}")
        for cat, dfs in merged.items():
            cat_label = CATEGORY_LABELS.get(cat, cat.replace("_", " ").title())
            with st.expander(f"📋 {cat_label}", expanded=False):
                for label, df in dfs.items():
                    st.markdown(f"**{label.replace('_', ' ').title()}**")
                    st.dataframe(df, use_container_width=True)
                    st.download_button(
                        label=f"📥 Baixar {label}",
                        data=df.to_csv(index=False),
                        file_name=f"mx_{label.replace(' · ', '_')}.csv",
                        mime="text/csv",
                        key=f"dl_{cat}_{label}",
                    )


if __name__ == "__main__":
    main()
