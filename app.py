from __future__ import annotations
import os

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# IMPORTAÇÕES RELACIONADAS AO SIM-DATASUS (main.ipynb)
# ============================================================================
from src.core.sim_visualizer import (
    plot_deaths_by_category,
    plot_deaths_by_age,
    plot_deaths_by_subcategory_and_age,
    plot_all_categories,
    get_category_statistics,
    compare_categories_distribution,
    load_sim_data_by_year,
    load_sim_data_range,
    combine_sim_data,
    plot_deaths_by_year,
    plot_category_comparison_by_year,
    plot_category_heatmap_by_year,
    plot_age_distribution_by_year,
    get_statistics_by_year,
    DICTIONARY_COLORS,
    DICTIONARY_LABELS,
    total_deaths_by_category,
)

# ============================================================================
# IMPORTAÇÕES NÃO RELACIONADAS AO MAIN.IPYNB (COMENTADAS)
# ============================================================================
# from main import config, load_data
# from src.core.visualizer import InsuranceVisualizer
 
st.set_page_config(
    layout="wide",
    page_title="Análise de Mortalidade SIM-DATASUS",
    page_icon="�",
)
# ============================================================================
# FUNÇÕES PARA CARREGAR DADOS PRÉ-CALCULADOS
# ============================================================================

def discover_available_analyses() -> Dict[str, List[str]]:
    """
    Descobre análises disponíveis na estrutura output/{population_source}/{year}/
    
    Returns:
    - Dicionário: {população_source: [anos]}
    """
    output_dir = Path("./output")
    analyses = {}
    
    if not output_dir.exists():
        return analyses
    
    for pop_source_dir in output_dir.iterdir():
        if pop_source_dir.is_dir():
            years = []
            for year_dir in pop_source_dir.iterdir():
                if year_dir.is_dir() and year_dir.name.isdigit():
                    years.append(year_dir.name)
            if years:
                analyses[pop_source_dir.name] = sorted(years, reverse=True)
    
    return analyses


def get_analysis_path(population_source: str, year: str) -> Path:
    """Retorna o caminho base da análise para uma população e ano específicos."""
    return Path("./output") / population_source / year


def load_deaths_data(population_source: str, year: str) -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os arquivos de morte da análise.
    
    Returns:
    - Dicionário com DataFrames: {'deaths_by_age', 'deaths_by_sex', ...}
    """
    base_path = get_analysis_path(population_source, year) / "deaths"
    deaths_data = {}
    
    if not base_path.exists():
        return deaths_data
    
    file_map = {
        '01_deaths_by_age': 'deaths_by_age',
        '02_deaths_by_age_and_sex': 'deaths_by_sex',
        '03_deaths_by_age_and_race': 'deaths_by_race',
        '04_deaths_by_age_and_education': 'deaths_by_education',
        '05_deaths_by_age_and_marital_status': 'deaths_by_marital',
    }
    
    for file_prefix, key in file_map.items():
        # Find file with this prefix
        matching_files = list(base_path.glob(f"{file_prefix}_*.csv"))
        if matching_files:
            deaths_data[key] = pd.read_csv(matching_files[0])
    
    return deaths_data


def load_mx_data(population_source: str, year: str) -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os arquivos de taxa de mortalidade (mx).
    
    Returns:
    - Dicionário com DataFrames: {'mx_total', 'mx_by_sex_masculino', ...}
    """
    base_path = get_analysis_path(population_source, year) / "mx"
    mx_data = {}
    
    if not base_path.exists():
        return mx_data
    
    # Load all mx files
    for file in base_path.glob("*.csv"):
        # Extract meaningful name from filename
        name = file.stem.split('_SIM-DATASUS')[0]  # Remove source suffix
        mx_data[name] = pd.read_csv(file)
    
    return mx_data


def load_summary_data(population_source: str, year: str) -> Optional[pd.DataFrame]:
    """Carrega dados de sumário estatístico."""
    base_path = get_analysis_path(population_source, year) / "summary"
    
    if not base_path.exists():
        return None
    
    files = list(base_path.glob("*.csv"))
    if files:
        return pd.read_csv(files[0])
    
    return None


# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO PARA DADOS PRÉ-CALCULADOS
# ============================================================================

def plot_deaths_chart(df: pd.DataFrame, title: str = "Óbitos por Idade") -> None:
    """Plota gráfico de óbitos por idade."""
    if 'idade' not in df.columns or 'deaths' not in df.columns:
        st.warning("Formato de dados inválido para este gráfico")
        return
    
    fig = px.line(
        df,
        x='idade',
        y='deaths',
        title=title,
        markers=True,
        labels={'idade': 'Idade', 'deaths': 'Total de Óbitos'}
    )
    
    fig.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)


def plot_deaths_by_category_chart(df: pd.DataFrame, title: str = "Óbitos por Categoria") -> None:
    """Plota gráfico de óbitos por categorias (sexo, raça, etc)."""
    if 'idade' not in df.columns:
        st.warning("Formato de dados inválido")
        return
    
    # Get all columns except 'idade'
    category_cols = [col for col in df.columns if col != 'idade']
    
    fig = go.Figure()
    
    for col in category_cols:
        fig.add_trace(go.Scatter(
            x=df['idade'],
            y=df[col],
            mode='lines+markers',
            name=col
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Idade',
        yaxis_title='Óbitos',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_mx_chart(df: pd.DataFrame, title: str = "Taxa de Mortalidade (mx)") -> None:
    """Plota gráfico de taxa de mortalidade."""
    if 'idade' not in df.columns or 'mx' not in df.columns:
        st.warning("Formato de dados inválido para mx")
        return
    
    fig = px.line(
        df,
        x='idade',
        y='mx',
        title=title,
        markers=True,
        labels={'idade': 'Idade', 'mx': 'Taxa de Mortalidade (mx)'}
    )
    
    fig.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)


def plot_mx_comparison_chart(mx_data: Dict[str, pd.DataFrame], title: str = "Comparação de mx") -> None:
    """Plota comparação de taxas de mortalidade por subcategorias."""
    fig = go.Figure()
    
    for name, df in mx_data.items():
        if 'idade' in df.columns and 'mx' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['idade'],
                y=df['mx'],
                mode='lines+markers',
                name=name.replace('08_mx_by_race_', '').replace('07_mx_by_sex_', '').capitalize()
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Idade',
        yaxis_title='Taxa de Mortalidade (mx)',
        height=500,
        hovermode='x unified',
        legend=dict(orientation='v', yanchor='top', y=0.99, xanchor='left', x=0.01)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_summary_table(summary_df: pd.DataFrame) -> None:
    """Exibe tabela de sumário estatístico."""
    st.subheader("📊 Sumário Estatístico")
    
    # Formata números para melhor legibilidade
    display_df = summary_df.copy()
    numeric_cols = display_df.select_dtypes(include=['float64', 'int64']).columns
    
    for col in numeric_cols:
        if 'percent' in col.lower():
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")
        elif 'deaths' in col.lower() or col == 'Total_Deaths':
            display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}")
        else:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(display_df, use_container_width=True)
# ============================================================================
# FUNÇÕES PARA VISUALIZAR DADOS PRÉ-CALCULADOS
# ============================================================================

def render_deaths_overview(deaths_data: Dict[str, pd.DataFrame]) -> None:
    """Renderiza visão geral de óbitos."""
    st.subheader("💀 Óbitos por Demográfico")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Idade",
        "Sexo",
        "Raça/Cor",
        "Escolaridade",
        "Estado Civil"
    ])
    
    with tab1:
        if 'deaths_by_age' in deaths_data:
            plot_deaths_chart(deaths_data['deaths_by_age'], "Total de Óbitos por Idade")
    
    with tab2:
        if 'deaths_by_sex' in deaths_data:
            plot_deaths_by_category_chart(deaths_data['deaths_by_sex'], "Óbitos por Sexo e Idade")
    
    with tab3:
        if 'deaths_by_race' in deaths_data:
            plot_deaths_by_category_chart(deaths_data['deaths_by_race'], "Óbitos por Raça/Cor e Idade")
    
    with tab4:
        if 'deaths_by_education' in deaths_data:
            plot_deaths_by_category_chart(deaths_data['deaths_by_education'], "Óbitos por Escolaridade e Idade")
    
    with tab5:
        if 'deaths_by_marital' in deaths_data:
            plot_deaths_by_category_chart(deaths_data['deaths_by_marital'], "Óbitos por Estado Civil e Idade")


def render_mx_overview(mx_data: Dict[str, pd.DataFrame]) -> None:
    """Renderiza visão geral de taxas de mortalidade."""
    st.subheader("📈 Taxa de Mortalidade (mx)")
    
    # Separate mx data by type
    total_mx = {k: v for k, v in mx_data.items() if 'total' in k}
    sex_mx = {k: v for k, v in mx_data.items() if 'sex' in k}
    race_mx = {k: v for k, v in mx_data.items() if 'race' in k}
    
    tab1, tab2, tab3 = st.tabs(["Total", "Por Sexo", "Por Raça/Cor"])
    
    with tab1:
        if total_mx:
            first_key = list(total_mx.keys())[0]
            plot_mx_chart(total_mx[first_key], "Taxa de Mortalidade - População Total")
    
    with tab2:
        if sex_mx:
            plot_mx_comparison_chart(sex_mx, "Comparação de mx por Sexo")
    
    with tab3:
        if race_mx:
            plot_mx_comparison_chart(race_mx, "Comparação de mx por Raça/Cor")


def render_analysis_dashboard(population_source: str, year: str) -> None:
    """Renderiza o dashboard completo com dados pré-calculados."""
    st.success(f"✅ Análise carregada: {population_source} ({year})")
    
    # Load all data
    deaths_data = load_deaths_data(population_source, year)
    mx_data = load_mx_data(population_source, year)
    summary_data = load_summary_data(population_source, year)
    
    if not deaths_data and not mx_data:
        st.error("❌ Nenhum dado encontrado para esta análise")
        return
    
    # Tabs for different views
    tab_deaths, tab_mx, tab_summary = st.tabs([
        "💀 Óbitos",
        "📈 Mortalidade (mx)",
        "📊 Sumário"
    ])
    
    with tab_deaths:
        if deaths_data:
            render_deaths_overview(deaths_data)
        else:
            st.info("Dados de óbitos não disponíveis")
    
    with tab_mx:
        if mx_data:
            render_mx_overview(mx_data)
        else:
            st.info("Dados de mortalidade não disponíveis")
    
    with tab_summary:
        if summary_data is not None:
            display_summary_table(summary_data)
        else:
            st.info("Dados de sumário não disponíveis")

# ============================================================================
# MAIN - ANÁLISE PRÉ-CALCULADA DE MORTALIDADE
# ============================================================================

def main():
    """Função principal que exibe análises de mortalidade pré-calculadas."""
    
    st.title("📊 Análise de Mortalidade - SIM-DATASUS")
    st.markdown("Visualização de análises de óbitos com dados pré-calculados")
    
    # Descobrir análises disponíveis
    analyses = discover_available_analyses()
    
    if not analyses:
        st.warning("⚠️ Nenhuma análise disponível em ./output/")
        st.info("""
        Para gerar análises, execute primeiro:
        ```bash
        python calculate_mortality_analysis.py
        ```
        """)
        return
    
    # Sidebar para seleção
    st.sidebar.header("⚙️ Seleção de Análise")
    
    # Selecionar população
    population_options = list(analyses.keys())
    selected_population = st.sidebar.selectbox(
        "📊 População",
        population_options,
        help="Selecione a fonte de dados populacionais"
    )
    
    # Selecionar ano
    year_options = analyses[selected_population]
    selected_year = st.sidebar.selectbox(
        "📅 Ano",
        year_options,
        help="Selecione o ano da análise"
    )
    
    st.markdown("---")
    
    # Renderizar análise selecionada
    render_analysis_dashboard(selected_population, selected_year)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**População:** {selected_population}")
    
    with col2:
        st.markdown(f"**Ano:** {selected_year}")
    
    with col3:
        st.markdown(f"**Atualizado:** {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")


if __name__ == "__main__":
    main()
