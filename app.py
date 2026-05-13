from __future__ import annotations

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional, Tuple

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
# FUNÇÕES RELACIONADAS AO SIM-DATASUS (main.ipynb)
# ============================================================================

def load_sim_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Carrega dados do arquivo SIM-DATASUS.
    
    Parameters:
    - file_path: Caminho do arquivo CSV
    
    Returns:
    - DataFrame ou None se houver erro
    """
    try:
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        st.error(f"❌ Arquivo não encontrado: {file_path}")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {str(e)}")
        return None


def render_summary_metrics(data: pd.DataFrame) -> None:
    """
    Renderiza métricas resumidas dos dados de mortalidade.
    
    Parameters:
    - data: DataFrame com dados de óbitos
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Óbitos", f"{len(data):,}")
    
    with col2:
        if 'sexo' in data.columns:
            masculino = len(data[data['sexo'] == 1])
            st.metric("Masculino", f"{masculino:,}")
        else:
            st.metric("Masculino", "N/A")
    
    with col3:
        if 'sexo' in data.columns:
            feminino = len(data[data['sexo'] == 2])
            st.metric("Feminino", f"{feminino:,}")
        else:
            st.metric("Feminino", "N/A")
    
    with col4:
        if 'idade' in data.columns:
            idade_media = data['idade'].mean()
            st.metric("Idade Média", f"{idade_media:.1f} anos")
        else:
            st.metric("Idade Média", "N/A")


def render_category_view(data: pd.DataFrame) -> None:
    """
    Renderiza análise por categoria.
    
    Parameters:
    - data: DataFrame com dados de óbitos
    """
    st.subheader("📊 Análise por Categoria")
    
    selected_category = st.selectbox(
        "Selecione a categoria",
        ["raca_cor", "sexo", "escolaridade", "estado_civil"]
    )
    
    plot_deaths_by_category(data, selected_category)
    
    st.markdown("---")
    st.subheader("📋 Estatísticas")
    stats = get_category_statistics(data, selected_category)
    st.dataframe(stats[['label', 'total_obitos', 'percentual']], use_container_width=True)


def render_age_view(data: pd.DataFrame) -> None:
    """
    Renderiza análise por idade com subcategorias.
    
    Parameters:
    - data: DataFrame com dados de óbitos
    """
    st.subheader("📈 Análise por Idade")
    
    age_visualization = st.radio(
        "Tipo de visualização",
        ["Total Geral", "Por Sexo", "Por Raça/Cor", "Por Escolaridade", "Por Estado Civil"]
    )
    
    visualization_map = {
        "Total Geral": lambda: plot_deaths_by_age(data),
        "Por Sexo": lambda: plot_deaths_by_subcategory_and_age(data, "sexo"),
        "Por Raça/Cor": lambda: plot_deaths_by_subcategory_and_age(data, "raca_cor"),
        "Por Escolaridade": lambda: plot_deaths_by_subcategory_and_age(data, "escolaridade"),
        "Por Estado Civil": lambda: plot_deaths_by_subcategory_and_age(data, "estado_civil"),
    }
    
    if age_visualization in visualization_map:
        visualization_map[age_visualization]()


def render_comparison_view(data: pd.DataFrame) -> None:
    """
    Renderiza comparação entre duas categorias.
    
    Parameters:
    - data: DataFrame com dados de óbitos
    """
    st.subheader("🔄 Comparações entre Categorias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cat1 = st.selectbox(
            "Primeira categoria",
            ["raca_cor", "sexo", "escolaridade", "estado_civil"],
            key="cat1"
        )
    
    with col2:
        cat2 = st.selectbox(
            "Segunda categoria",
            ["sexo", "raca_cor", "escolaridade", "estado_civil"],
            key="cat2"
        )
    
    compare_categories_distribution(data, cat1, cat2)


def render_details_view(data: pd.DataFrame) -> None:
    """
    Renderiza análise detalhada dos dados.
    
    Parameters:
    - data: DataFrame com dados de óbitos
    """
    st.subheader("🔍 Análise Detalhada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Colunas do Dataset**")
        st.write(list(data.columns))
    
    with col2:
        st.markdown("**Dimensões**")
        st.write(f"Linhas: {len(data):,}")
        st.write(f"Colunas: {len(data.columns)}")
    
    st.markdown("---")
    st.markdown("**Amostra dos Dados**")
    st.dataframe(data.head(10), use_container_width=True)
    
    st.markdown("---")
    st.markdown("**Estatísticas Descritivas**")
    st.dataframe(data.describe(), use_container_width=True)


def render_sim_dashboard(sim_data_path: str) -> None:
    """
    Renderiza o dashboard completo de análise de mortalidade SIM-DATASUS.
    
    Parameters:
    - sim_data_path: Caminho do arquivo de dados
    """
    sim_data = load_sim_data(sim_data_path)
    
    if sim_data is None:
        st.info("Verifique se o caminho do arquivo está correto.")
        return
    
    st.success(f"✅ Dados carregados: {len(sim_data):,} registros")
    
    sim_view_type = st.sidebar.radio(
        "Tipo de Visualização",
        ["Resumo Geral", "Por Categoria", "Por Idade", "Comparações", "Detalhes"]
    )
    
    if sim_view_type == "Resumo Geral":
        st.subheader("📈 Resumo Geral de Óbitos")
        render_summary_metrics(sim_data)
        st.markdown("---")
        plot_all_categories(sim_data)
    
    elif sim_view_type == "Por Categoria":
        render_category_view(sim_data)
    
    elif sim_view_type == "Por Idade":
        render_age_view(sim_data)
    
    elif sim_view_type == "Comparações":
        render_comparison_view(sim_data)
    
    elif sim_view_type == "Detalhes":
        render_details_view(sim_data)


def render_comparative_analysis() -> None:
    """
    Renderiza análise comparativa entre múltiplos anos (2004-2022).
    """
    st.subheader("📊 Análise Comparativa por Ano (2004-2022)")
    
    # Configurações
    col1, col2 = st.columns(2)
    
    with col1:
        year_start = st.slider("Ano Inicial", min_value=2004, max_value=2022, value=2010)
    
    with col2:
        year_end = st.slider("Ano Final", min_value=2004, max_value=2022, value=2022)
    
    if year_start > year_end:
        st.error("❌ Ano inicial não pode ser maior que ano final")
        return
    
    base_path = "//Projetos2/Wrk/SIM-DATASUS/MICRODADOS"
    
    # Carrega dados para o intervalo
    st.info(f"⏳ Carregando dados de {year_start} a {year_end}...")
    dfs = load_sim_data_range(base_path, year_start, year_end)
    
    if not dfs:
        st.error("❌ Nenhum dado disponível para o período selecionado")
        return
    
    # Tipo de análise comparativa
    comparative_type = st.radio(
        "Tipo de Análise Comparativa",
        [
            "Evolução Geral de Óbitos",
            "Evolução por Categoria",
            "Heatmap de Categoria",
            "Distribuição Etária",
            "Estatísticas Gerais"
        ]
    )
    
    st.markdown("---")
    
    if comparative_type == "Evolução Geral de Óbitos":
        st.markdown("**Análise**: Tendência geral de óbitos ao longo dos anos")
        plot_deaths_by_year(dfs)
    
    elif comparative_type == "Evolução por Categoria":
        st.markdown("**Análise**: Como cada subcategoria evoluiu ao longo dos anos")
        
        category = st.selectbox(
            "Selecione a categoria",
            ["raca_cor", "sexo", "escolaridade", "estado_civil"]
        )
        
        plot_category_comparison_by_year(dfs, category)
    
    elif comparative_type == "Heatmap de Categoria":
        st.markdown("**Análise**: Mapa de calor mostrando intensidade de óbitos por categoria e ano")
        
        category = st.selectbox(
            "Selecione a categoria",
            ["raca_cor", "sexo", "escolaridade", "estado_civil"],
            key="heatmap_category"
        )
        
        plot_category_heatmap_by_year(dfs, category)
    
    elif comparative_type == "Distribuição Etária":
        st.markdown("**Análise**: Como a distribuição por idade mudou entre anos")
        plot_age_distribution_by_year(dfs)
    
    elif comparative_type == "Estatísticas Gerais":
        st.markdown("**Análise**: Resumo estatístico completo por ano")
        
        # Seleciona se quer detalhar por categoria
        col1, col2 = st.columns(2)
        
        with col1:
            include_category = st.checkbox("Detalhar por categoria?")
        
        with col2:
            detail_category = None
            if include_category:
                detail_category = st.selectbox(
                    "Categoria para detalhe",
                    ["raca_cor", "sexo", "escolaridade", "estado_civil"],
                    key="stats_category"
                )
        
        stats_df = get_statistics_by_year(dfs, detail_category if include_category else None)
        
        st.dataframe(stats_df, use_container_width=True)
        
        # Download CSV
        csv = stats_df.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Estatísticas (CSV)",
            data=csv,
            file_name=f"estatisticas_sim_{year_start}_{year_end}.csv",
            mime="text/csv"
        )


# ============================================================================
# MAIN - ANÁLISE DE MORTALIDADE SIM-DATASUS
# ============================================================================

def main():
    """Função principal que executa o aplicativo de análise SIM-DATASUS."""
    
    st.title("📊 Análise de Mortalidade - SIM-DATASUS")
    st.markdown("Visualização e análise de dados de óbitos do Sistema de Informação sobre Mortalidade")
    
    # Sidebar para configurações
    st.sidebar.header("⚙️ Configurações")
    
    # Seleção de modo de análise
    analysis_mode = st.sidebar.radio(
        "Modo de Análise",
        ["Ano Único", "Comparativo (2004-2022)"]
    )
    
    st.markdown("---")
    
    if analysis_mode == "Ano Único":
        # Input do caminho do arquivo
        sim_data_path = st.sidebar.text_input(
            "Caminho do arquivo SIM-DATASUS",
            value="//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/SIM-DATASUS-2020.csv",
            help="Insira o caminho completo do arquivo CSV com dados de mortalidade"
        )
        
        # Renderiza o dashboard
        render_sim_dashboard(sim_data_path)
    
    else:  # Comparativo
        # Renderiza análise comparativa
        render_comparative_analysis()
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Última atualização:** {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")


if __name__ == "__main__":
    main()
