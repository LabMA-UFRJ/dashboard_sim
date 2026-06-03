from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import plotly.graph_objects as go

st.set_page_config(
    layout="wide",
    page_title="Análise de Mortalidade SIM-DATASUS",
    page_icon="📊",
)

# ============================================================================
# CARREGAMENTO DE DADOS MX
# ============================================================================

@st.cache_data
def load_mx_files():
    """Carrega todos os arquivos de mx dos dados raw."""
    raw_data_dir = Path("./data/raw")
    mx_files = {}

    if raw_data_dir.exists():
        for file in raw_data_dir.glob("mx_*.csv"):
            name = file.stem.replace("mx_", "").replace("_todos_anos", "")
            try:
                # utf-8-sig remove BOM automaticamente
                df = pd.read_csv(file, encoding='utf-8-sig', on_bad_lines='skip')
                df.columns = df.columns.str.strip()
            except Exception as e:
                st.warning(f"Erro ao ler {name}: {e}")
                continue

            mx_files[name] = df

    return mx_files


def get_years_available(mx_data: Dict[str, pd.DataFrame]) -> list:
    """Extrai todos os anos disponíveis dos dados mx."""
    years = set()
    for df in mx_data.values():
        if 'ano' in df.columns:
            years.update(df['ano'].unique())
    return sorted(years, reverse=True)


def get_mx_by_year(mx_data: Dict[str, pd.DataFrame], year: int) -> Dict[str, pd.DataFrame]:
    """Filtra dados de mx para um ano específico."""
    mx_by_year = {}
    for name, df in mx_data.items():
        if 'ano' in df.columns:
            filtered = df[df['ano'] == year].copy()
            if not filtered.empty:
                mx_by_year[name] = filtered
    return mx_by_year


# ============================================================================
# FUNÇÕES DE ESTATÍSTICAS
# ============================================================================

def calculate_statistics(df: pd.DataFrame) -> Dict:
    """Calcula estatísticas para um dataframe de mx."""
    if 'Mx' not in df.columns:
        return {}
    
    mx_values = df['Mx'].dropna()
    
    stats = {
        'Média': mx_values.mean(),
        'Mediana': mx_values.median(),
        'Mínimo': mx_values.min(),
        'Máximo': mx_values.max(),
        'Desvio Padrão': mx_values.std(),
        'Total de Óbitos': df['obitos'].sum() if 'obitos' in df.columns else 0,
        'Total de Exposição': df['exposicao'].sum() if 'exposicao' in df.columns else 0,
    }
    
    return stats


# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================

_ORDEM_ESCOLARIDADE = [
    "SEM ESCOLARIDADE",
    "FUNDAMENTAL INCOMPLETO",
    "FUNDAMENTAL COMPLETO",
    "MEDIO COMPLETO",
    "SUPERIOR INCOMPLETO",
    "SUPERIOR COMPLETO",
]

_CORES_SEXO = {'FEMININO': '#FF6B6B', 'MASCULINO': '#4ECDC4'}


def plot_mx_idade(df: pd.DataFrame, year: int) -> None:
    """Mx por Idade — linha em escala log, x de 16 a 100."""
    plot_data = df[df['Mx'] > 0].sort_values('idade_num')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=plot_data['idade_num'],
        y=plot_data['Mx'],
        mode='lines',
        line=dict(color='blue', width=1.5),
        hovertemplate='Idade: %{x}<br>Mx: %{y:.6f}<extra></extra>',
    ))
    fig.update_layout(
        title=f'Taxa Central de Mortalidade (Mx) por Idade - Brasil {year}',
        xaxis=dict(title='Idade (anos)', range=[16, 100]),
        yaxis=dict(title='Mx (escala log)', type='log'),
        height=500,
        hovermode='x unified',
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_mx_sexo(df: pd.DataFrame, year: int) -> None:
    """Mx por Sexo — barras apenas MASCULINO/FEMININO com valores anotados."""
    plot_data = df[df['sexo'].isin(['MASCULINO', 'FEMININO'])].copy()
    plot_data['cor'] = plot_data['sexo'].map(_CORES_SEXO)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plot_data['sexo'],
        y=plot_data['Mx'],
        marker_color=plot_data['cor'],
        text=plot_data['Mx'].apply(lambda v: f'{v:.5f}'),
        textposition='outside',
        hovertemplate='%{x}<br>Mx: %{y:.6f}<extra></extra>',
    ))
    fig.update_layout(
        title=f'Taxa Central de Mortalidade (Mx) por Sexo - Brasil {year}',
        xaxis_title='Sexo',
        yaxis_title='Mx',
        height=450,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_mx_uf(df: pd.DataFrame, year: int) -> None:
    """Mx por UF — barras horizontais ordenadas crescente."""
    plot_data = df.sort_values('Mx', ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=plot_data['uf'],
        x=plot_data['Mx'],
        orientation='h',
        marker_color='steelblue',
        hovertemplate='%{y}<br>Mx: %{x:.6f}<extra></extra>',
    ))
    fig.update_layout(
        title=f'Taxa Central de Mortalidade (Mx) por UF - Brasil {year}',
        xaxis_title='Mx',
        yaxis_title='',
        height=max(500, len(plot_data) * 22),
        hovermode='y unified',
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_mx_estado_civil(df: pd.DataFrame, year: int) -> None:
    """Mx por Estado Civil — barras ordenadas decrescente, sem NÃO INFORMADO."""
    plot_data = df[df['estado_civil'] != 'NÃO INFORMADO'].sort_values('Mx', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plot_data['estado_civil'],
        y=plot_data['Mx'],
        marker_color='coral',
        hovertemplate='%{x}<br>Mx: %{y:.6f}<extra></extra>',
    ))
    fig.update_layout(
        title=f'Taxa Central de Mortalidade (Mx) por Estado Civil - Brasil {year}',
        xaxis=dict(title='', tickangle=-45),
        yaxis_title='Mx',
        height=500,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_mx_escolaridade(df: pd.DataFrame, year: int) -> None:
    """Mx por Escolaridade — barras na ordem educacional crescente."""
    plot_data = df[df['escolaridade'].isin(_ORDEM_ESCOLARIDADE)].copy()
    plot_data['ordem'] = plot_data['escolaridade'].map(
        {v: i for i, v in enumerate(_ORDEM_ESCOLARIDADE)}
    )
    plot_data = plot_data.sort_values('ordem')

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=plot_data['escolaridade'],
        y=plot_data['Mx'],
        marker_color='mediumseagreen',
        hovertemplate='%{x}<br>Mx: %{y:.6f}<extra></extra>',
    ))
    fig.update_layout(
        title=f'Taxa Central de Mortalidade (Mx) por Escolaridade - Brasil {year}',
        xaxis=dict(title='', tickangle=-45),
        yaxis_title='Mx',
        height=500,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.title("📊 Análise de Mortalidade - Taxas (Mx) por Ano")
    st.markdown("Visualização simplificada das taxas de mortalidade (mx) do SIM-DATASUS por ano")
    
    # Carregar dados
    mx_data = load_mx_files()
    
    if not mx_data:
        st.error("❌ Nenhum arquivo de mx encontrado em data/raw/")
        return
    
    # Selecionar ano
    available_years = get_years_available(mx_data)
    selected_year: Optional[int] = st.sidebar.selectbox(
        "📅 Selecione o Ano",
        available_years,
        help="Escolha o ano para análise"
    )

    if selected_year is None:
        st.info("Nenhum ano disponível.")
        return

    # Filtrar dados para o ano selecionado
    mx_by_year = get_mx_by_year(mx_data, selected_year)
    
    if not mx_by_year:
        st.error(f"❌ Nenhum dado disponível para o ano {selected_year}")
        return
    
    st.success(f"✅ Dados carregados para o ano {selected_year}")
    st.markdown("---")
    
    # Abas para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["📈 Visualizações", "📊 Estatísticas", "📋 Dados"])
    
    with tab1:
        st.subheader(f"Visualizações - {selected_year}")
        
        # Mostrar dados por tipo
        for category_name, df in mx_by_year.items():
            with st.expander(f"📊 {category_name.upper().replace('_', ' ')}", expanded=True):
                if 'idade_num' in df.columns:
                    plot_mx_idade(df, selected_year)
                elif 'sexo' in df.columns:
                    plot_mx_sexo(df, selected_year)
                elif 'escolaridade' in df.columns:
                    plot_mx_escolaridade(df, selected_year)
                elif 'estado_civil' in df.columns:
                    plot_mx_estado_civil(df, selected_year)
                elif 'uf' in df.columns:
                    plot_mx_uf(df, selected_year)
    
    with tab2:
        st.subheader(f"Estatísticas por Categoria - {selected_year}")
        
        # Mostrar estatísticas por categoria
        for category_name, df in mx_by_year.items():
            stats = calculate_statistics(df)
            
            if stats:
                with st.expander(f"📈 {category_name.upper().replace('_', ' ')}", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Média Mx", f"{stats['Média']:.6f}")
                    with col2:
                        st.metric("Mediana Mx", f"{stats['Mediana']:.6f}")
                    with col3:
                        st.metric("Mínimo Mx", f"{stats['Mínimo']:.6f}")
                    with col4:
                        st.metric("Máximo Mx", f"{stats['Máximo']:.6f}")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Desvio Padrão", f"{stats['Desvio Padrão']:.6f}")
                    with col2:
                        st.metric("Total Óbitos", f"{int(stats['Total de Óbitos']):,}")
                    with col3:
                        st.metric("Total Exposição", f"{int(stats['Total de Exposição']):,}")
    
    with tab3:
        st.subheader(f"Dados Brutos - {selected_year}")
        
        # Mostrar dados brutos
        for category_name, df in mx_by_year.items():
            with st.expander(f"📋 {category_name.upper().replace('_', ' ')}", expanded=False):
                st.dataframe(df, use_container_width=True)
                
                # Botão para download
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Baixar {category_name.upper()}",
                    data=csv,
                    file_name=f"mx_{category_name}_{selected_year}.csv",
                    mime="text/csv"
                )


if __name__ == "__main__":
    main()
